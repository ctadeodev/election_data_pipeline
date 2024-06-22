import os
import time
import random
import logging

import requests
import psycopg2

from config import VOTERS_TURNOUT, CANDIDATE_VOTE_WEIGHTS


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = 'http://localhost:5000/vote'


def set_expected_voters_turnout(ratio):
    voter_counts = {}
    for state, (_, voters_turnout, _) in VOTERS_TURNOUT.items():
        voter_counts[state] = int(voters_turnout * ratio)
    return voter_counts


def get_pending_voters(expected_voter_turnout, current_voters_turnout):
    pending_voters_count = {}
    for state in expected_voter_turnout:
        if state not in current_voters_turnout:
            pending_voters_count[state] = expected_voter_turnout[state]
            continue
        pending_voters_count[state] = expected_voter_turnout[state] - current_voters_turnout[state]
        if pending_voters_count[state] < 1:
            pending_voters_count.pop(state)
    return pending_voters_count


def get_current_voters_turnout(cur, election_id):
    cur.execute("""
        SELECT
            v2.state,
            count(1)
        FROM votes v
        JOIN voters v2 ON v.voter_id = v2.voter_id AND v.election_id = %s
        GROUP BY v2.state
    """, (election_id, ))
    return dict(cur.fetchall())


def select_candidate_weighted(candidate_ids, state):
    candidate_probs = CANDIDATE_VOTE_WEIGHTS[state]
    weights = candidate_probs
    return random.choices(candidate_ids, weights=weights, k=1)[0]


def produce_voting_events(election_id, batch_size=200):
    conn = psycopg2.connect(
        dbname=os.environ['PG_DB'],
        user=os.environ['PG_USER'],
        password=os.environ['PG_PASSWORD'],
        host=os.environ['PG_HOST'],
        port='5432'
    )
    cur = conn.cursor()
    cur.execute("""SELECT candidate_id FROM candidates WHERE election_id = %s""", (election_id, ))
    candidate_ids = [data[0] for data in cur.fetchall()]
    expected_voter_turnout = set_expected_voters_turnout(1 / 10000)
    offset = 0
    try:
        while True:
            pending_voters_count = get_pending_voters(
                expected_voter_turnout,
                get_current_voters_turnout(cur, election_id)
            )
            if not pending_voters_count:
                break
            cur.execute("""
                SELECT v.voter_id, v.state
                FROM voters v
                LEFT JOIN votes vo ON v.voter_id = vo.voter_id AND vo.election_id = %s
                WHERE vo.voter_id IS NULL AND v.state IN %s
                ORDER BY v.voter_id
                LIMIT %s
                OFFSET %s
            """, (election_id, tuple(pending_voters_count), batch_size, offset))
            rows = cur.fetchall()
            if not rows:
                logger.info("Stopped voting events. No more voters available")
                break

            if len(rows) < batch_size:
                offset = 0
            else:
                offset += batch_size
            for row in rows:
                voter_id, state = row
                if state in pending_voters_count:
                    pending_voters_count[state] -= 1
                    if not pending_voters_count[state]:
                        pending_voters_count.pop(state)
                else:
                    continue
                event = {
                    'voter_id': voter_id,
                    'election_id': election_id,
                    'candidate_id': select_candidate_weighted(candidate_ids, state)
                }
                requests.post(API_URL, json=event)
                logger.info("Produced registration event: %s", event)
                time.sleep(0.1)

            time.sleep(random.randint(3, 5))
    except KeyboardInterrupt:
        pass
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    produce_voting_events(1)
