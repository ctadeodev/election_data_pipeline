import json
import logging
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_batch
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def consume_registration_events(batch_size=500):
    consumer = KafkaConsumer(
        'registration',
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

    insert_query = """
    INSERT INTO voters (full_name, registration_date, dob, gender, state)
    VALUES (%s, %s, %s, %s, %s)
    """
    batch = []
    while True:
        try:
            for message in consumer.poll(timeout_ms=1000).values():
                for record in message:
                    try:
                        voter = record.value['voter']
                        full_name = voter['full_name']
                        # registration_date = datetime.strptime(voter['registered'], "%Y-%m-%dT%H:%M:%S.%fZ")
                        registration_date = voter['registered']
                        dob = datetime.strptime(voter['dob'].split('T')[0], "%Y-%m-%d").date()
                        dob = voter['dob']
                        gender = voter['gender'][0].upper()  # Ensure gender is 'M' or 'F',
                        state = voter['state']

                        batch.append((full_name, registration_date, dob, gender, state))
                        logging.info('Received registration event: %s (%s)', full_name, state)

                        # Check batch size and insert if batch is full
                        if len(batch) >= batch_size:
                            execute_batch(cur, insert_query, batch)
                            conn.commit()
                            logger.info("Inserted batch of %s registration events.", len(batch))
                            batch = []  # Clear batch after inserting

                    except Exception as e:
                        logger.error("Error processing registration event: %s", str(e))
                        conn.rollback()
        except KeyboardInterrupt:
            # Insert any remaining records in batch before shutting down
            if batch:
                execute_batch(cur, insert_query, batch)
                conn.commit()
                logger.info("Inserted final batch of %s registration events.", len(batch))
            break
    consumer.close()
    cur.close()
    conn.close()


if __name__ == '__main__':
    consume_registration_events()
