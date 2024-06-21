FROM apache/airflow:2.9.2-python3.11

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git libpq-dev build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
USER airflow

ADD requirements.txt .
RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt