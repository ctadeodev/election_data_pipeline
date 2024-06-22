import os
import json
import logging

import psycopg2
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


INSERT_QUERY = """
INSERT INTO votes (voter_id, candidate_id, election_id)
VALUES (%s, %s, %s)
ON CONFLICT (voter_id, election_id) DO NOTHING
"""

def consume_voting_events():
    consumer = KafkaConsumer(
        'vote',
        bootstrap_servers=os.environ['KAFKA_BROKER'],
        auto_offset_reset='earliest',
        api_version=(2, 5, 0),
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    conn = psycopg2.connect(
        dbname=os.environ['PG_DB'],
        user=os.environ['PG_USER'],
        password=os.environ['PG_PASSWORD'],
        host=os.environ['PG_HOST'],
        port="5432"
    )
    cur = conn.cursor()
    try:
        for message in consumer:
            voting_event = message.value
            voter_id = voting_event['voter_id']
            candidate_id = voting_event['candidate_id']
            election_id = voting_event['election_id']
            try:
                cur.execute(INSERT_QUERY, (voter_id, candidate_id, election_id))
                conn.commit()
                logging.info("[offset: %s]Stored vote from voter %s for candidate %s in election %s",
                             message.offset, voter_id, candidate_id, election_id)
            except psycopg2.Error as e:
                conn.rollback()
                logging.error("Error storing vote: %s", str(e))
    except KeyboardInterrupt:
        pass
    finally:
        print('Finished consuming')
        consumer.close()
        cur.close()
        conn.close()


if __name__ == '__main__':
    consume_voting_events()
