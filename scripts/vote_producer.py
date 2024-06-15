import json
import random
import logging

import psycopg2
from kafka import KafkaProducer

from config import VOTERS_TURNOUT, CANDIDATE_VOTE_WEIGHTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def set_voter_turnout_counts_per_state(ratio):
    voter_counts = {}
    for state, (_, voters_turnout, _) in VOTERS_TURNOUT.items():
        voter_counts[state] = int(voters_turnout * ratio)
    return voter_counts


def update_voter_turnout_counts_per_state(expected_voter_turnout, actual_voters_turnout):
    for state in expected_voter_turnout:
        if state not in actual_voters_turnout:
            continue
        expected_voter_turnout[state] -= actual_voters_turnout[state]
        if expected_voter_turnout[state] < 1:
            expected_voter_turnout.pop(state)
    return expected_voter_turnout


def get_actual_voters_turnout(cur, election_id):
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
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname='election_db',
        user='user',
        password='password',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()

    # Query to fetch voters not yet voted in the specified election_id
    cur.execute("""SELECT candidate_id FROM candidates WHERE election_id = %s""", (election_id, ))
    candidate_ids = [data[0] for data in cur.fetchall()]

    # Initialize Kafka producer (example, replace with your Kafka configuration)
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    try:
        offset = 0
        while True:
            # Query to fetch voters not yet voted in the specified election_id
            # cur.execute("""
            #     SELECT
            #         v.voter_id,
            #         v.state
            #     FROM voters v
            #     LEFT JOIN votes vo ON v.voter_id = vo.voter_id AND vo.election_id = %s
            #     WHERE vo.voter_id IS NULL
            #       AND v.state IN %s
            #     ORDER BY v.voter_id
            # """, (election_id, tuple(voter_turnout)))
            cur.execute("""
                SELECT voter_id, state
                FROM voters
                LIMIT %s
                OFFSET %s
            """, (batch_size, offset))
            offset += batch_size

            rows = cur.fetchall()
            if not rows:
                logger.info("Stopped voting events. No more voters available")
                break
            for row in rows:
                voter_id, state = row
                # Create voting event/message
                event = {
                    'voter_id': voter_id,
                    'election_id': election_id,
                    'state': state,
                    'candidate_id': select_candidate_weighted(candidate_ids, state)
                }

                producer.send('vote', value=event)
                logger.info("Produced registration event: %s", event)
    except KeyboardInterrupt:
        pass
    finally:
        # Close cursor and connection
        cur.close()
        conn.close()
        # Flush and close Kafka producer
        producer.flush()
        producer.close()


if __name__ == '__main__':
    produce_voting_events(1)
