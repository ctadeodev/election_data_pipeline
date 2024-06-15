import json
import logging

import psycopg2
from kafka import KafkaConsumer

from config import VOTERS_TURNOUT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def set_voter_turnout_counts_per_state(ratio):
    voter_counts = {}
    for state, (_, voters_turnout, _) in VOTERS_TURNOUT.items():
        voter_counts[state] = int(voters_turnout * ratio)
    return voter_counts


def consume_voting_events():
    consumer = KafkaConsumer(
        'vote',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    conn = psycopg2.connect(
        dbname="election_db",
        user="user",
        password="password",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    voter_turnout = set_voter_turnout_counts_per_state(1 / 10000)
    try:
        # Consume messages from Kafka topic indefinitely
        for message in consumer:
            if not voter_turnout:
                logger.info("Voter turnout reached")
                break
            voting_event = message.value

            # Extract data from voting event message
            voter_id = voting_event['voter_id']
            candidate_id = voting_event['candidate_id']
            election_id = voting_event['election_id']
            state = voting_event['state']
            if state not in voter_turnout:
                continue

            # Store the vote in the PostgreSQL database
            try:
                cur.execute("""
                    INSERT INTO votes (voter_id, candidate_id, election_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (voter_id, election_id) DO NOTHING
                """, (voter_id, candidate_id, election_id))
                conn.commit()
                logging.info("[offset: %s]Stored vote from voter %s for candidate %s in election %s",
                             message.offset, voter_id, candidate_id, election_id)
            except psycopg2.Error as e:
                conn.rollback()
                logging.error("Error storing vote: %s", str(e))
            else:
                voter_turnout[state] -= 1
                if not voter_turnout[state]:
                    voter_turnout.pop(state)
    except KeyboardInterrupt:
        pass
    finally:
        # Close Kafka consumer
        print('Finished consuming')
        consumer.close()

        # Close PostgreSQL cursor and connection
        cur.close()
        conn.close()


if __name__ == '__main__':
    consume_voting_events()
