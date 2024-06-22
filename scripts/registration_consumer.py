import os
import json
import logging
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_batch
from kafka import KafkaConsumer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INSERT_QUERY = """
INSERT INTO voters (full_name, registration_date, dob, gender, state)
VALUES (%s, %s, %s, %s, %s)
"""


def do_execute_batch(cur, conn, batch):
    execute_batch(cur, INSERT_QUERY, batch)
    conn.commit()
    logger.info("Inserted batch of %s registration events.", len(batch))


def consume_registration_events(batch_size=500):
    consumer = KafkaConsumer(
        'registration',
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
    batch = []
    while True:
        try:
            messages = consumer.poll(timeout_ms=1000)
            if not messages:
                if batch:
                    do_execute_batch(cur, conn, batch)
                    batch = []
                continue

            for message in messages.values():
                for record in message:
                    try:
                        voter = record.value['voter']
                        full_name = voter['full_name']
                        registration_date = voter['registered']
                        dob = datetime.strptime(voter['dob'].split('T')[0], "%Y-%m-%d").date()
                        dob = voter['dob']
                        gender = voter['gender'][0].upper()
                        state = voter['state']
                        batch.append((full_name, registration_date, dob, gender, state))
                        logging.info('Received registration event: %s (%s)', full_name, state)
                        if len(batch) >= batch_size:
                            do_execute_batch(cur, conn, batch)
                            batch = []
                    except Exception as e:
                        logger.error("Error processing registration event: %s", str(e))
                        conn.rollback()
        except KeyboardInterrupt:
            if batch:
                do_execute_batch(cur, conn, batch)
            break
    consumer.close()
    cur.close()
    conn.close()


if __name__ == '__main__':
    consume_registration_events()
