#!/bin/bash
nohup python /app/scripts/registration_consumer.py > /app/scripts/registration_consumer.log 2>&1 &
nohup python /app/scripts/vote_consumer.py > /app/scripts/vote_consumer.log 2>&1 &
exec python app.py