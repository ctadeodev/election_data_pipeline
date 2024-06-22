import os
from datetime import timedelta

from airflow.utils.dates import days_ago
from cosmos import (
    DbtDag,
    ProjectConfig,
    ProfileConfig,
    ExecutionConfig
)
from cosmos.profiles import SnowflakeUserPasswordProfileMapping

# Translate snowflake connection into dbt profile
profile_config = ProfileConfig(
    profile_name='default',
    target_name='dev',
    profile_mapping=SnowflakeUserPasswordProfileMapping('snowflake_conn')
)

dbt_snowflake_dag = DbtDag(
    project_config=ProjectConfig('/opt/airflow/dags/dbt/election_data_pipeline',),
    operator_args={'install_deps': True},
    profile_config=profile_config,
    execution_config=ExecutionConfig(dbt_executable_path=f"{os.environ['VIRTUAL_ENV']}/bin/dbt",),
    schedule_interval=timedelta(minutes=5),
    start_date=days_ago(1),
    catchup=False,
    dag_id='dbt_transform_dag'
)
