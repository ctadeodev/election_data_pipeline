FROM apache/airflow:latest

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git libpq-dev build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /opt/airflow
