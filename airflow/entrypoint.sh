#!/usr/bin/env bash

# Initialize the Airflow database if it hasn't been initialized already
airflow db init

# Start the scheduler in the background
airflow scheduler &

# Run the original command
exec airflow webserver
