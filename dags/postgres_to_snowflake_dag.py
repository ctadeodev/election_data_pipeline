import os
from datetime import timedelta

import pandas as pd

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}

dag = DAG(
    'postgres_to_snowflake_incremental',
    default_args=default_args,
    description='Incrementally load tables from PostgreSQL to Snowflake',
    schedule_interval=timedelta(minutes=1),
    start_date=days_ago(1),
    catchup=False,
    tags=['incremental_load', 'postgres', 'snowflake'],
)


def extract_data_from_postgres(table, logical_date):
    # Task 1: Extract data from PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='postgres_conn')
    query = 'SELECT last_pull_time FROM last_pull_info WHERE table_name = %s'
    last_updated_at = pg_hook.get_first(query, parameters=[table])[0]
    query = f'SELECT * FROM {table} WHERE updated_at > %s AND updated_at <= %s'
    df = pg_hook.get_pandas_df(query, parameters=[last_updated_at, logical_date])
    if df.empty:
        return f'skip_{table}_table'
    df.to_csv(f'/tmp/{table}.csv', index=False)
    return f'stage_{table}_data_files_to_snowflake'

def stage_data_files_to_snowflake(table):
    # Task 2: Stage Data Files to Snowflake Internal Stage
    file_path = f'/tmp/{table}.csv'
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_raw_conn')
    snowflake_hook.run(f"PUT file://{file_path} @%{table} OVERWRITE=TRUE;")
    os.remove(file_path)

def copy_staged_data_files_to_snowflake(table):
    # Task 3: Copy staged files to Snowflake table
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_raw_conn')
    query = f"""
        COPY INTO {table}
        FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"' SKIP_HEADER = 1);
    """
    snowflake_hook.run(query)

def update_last_pull_info(table, logical_date):
    # Task 4: update last_pull_info for postgresql table
    pg_hook = PostgresHook(postgres_conn_id='postgres_conn')
    update_query = 'UPDATE last_pull_info SET last_pull_time = %s WHERE table_name = %s'
    pg_hook.run(update_query, parameters=[logical_date, table])


start = EmptyOperator(task_id='start', dag=dag)

tables = ['voters', 'elections', 'candidates', 'votes']
for table in tables:
    extract_data = BranchPythonOperator(
        task_id=f'extract_{table}_data_from_postgres',
        python_callable=extract_data_from_postgres,
        op_kwargs={'table': table, 'logical_date': '{{ logical_date }}'},
        dag=dag,
    )

    skip_task = PythonOperator(
        task_id=f'skip_{table}_table',
        python_callable=lambda: print(f'No data to stage for {table}'),
        dag=dag,
    )

    stage_data = PythonOperator(
        task_id=f'stage_{table}_data_files_to_snowflake',
        python_callable=stage_data_files_to_snowflake,
        op_kwargs={'table': table},
        dag=dag,
    )
    
    copy_data = PythonOperator(
        task_id=f'copy_staged_{table}_data_to_snowflake',
        python_callable=copy_staged_data_files_to_snowflake,
        op_kwargs={'table': table},
        dag=dag,
    )
    
    update_metadata = PythonOperator(
        task_id=f'update_{table}_last_pull_info',
        python_callable=update_last_pull_info,
        op_kwargs={'table': table},
        dag=dag,
    )

    start >> extract_data >> [skip_task, stage_data]
    stage_data >> copy_data >> update_metadata
