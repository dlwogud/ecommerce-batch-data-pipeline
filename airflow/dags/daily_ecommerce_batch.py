from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_DIR = "/opt/airflow/project"
DBT_DIR = f"{PROJECT_DIR}/dbt"

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
}


with DAG(
    dag_id="daily_ecommerce_batch",
    description="Daily batch pipeline for fashion ecommerce sales mart",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["ecommerce", "batch", "dbt"],
) as dag:
    load_source_data = BashOperator(
        task_id="load_source_data",
        bash_command=f"cd {PROJECT_DIR} && python scripts/airflow_load_source_data.py",
        execution_timeout=timedelta(minutes=10),
    )

    incremental_load_source_to_raw = BashOperator(
        task_id="incremental_load_source_to_raw",
        bash_command=f"cd {PROJECT_DIR} && python scripts/airflow_incremental_load_source_to_raw.py",
        execution_timeout=timedelta(minutes=10),
    )

    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=f"cd {DBT_DIR} && dbt run --select staging --profiles-dir .",
        execution_timeout=timedelta(minutes=10),
    )

    dbt_test_staging = BashOperator(
        task_id="dbt_test_staging",
        bash_command=f"cd {DBT_DIR} && dbt test --select staging --profiles-dir .",
        execution_timeout=timedelta(minutes=10),
    )

    dbt_run_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=f"cd {DBT_DIR} && dbt run --select marts --profiles-dir .",
        execution_timeout=timedelta(minutes=10),
    )

    dbt_test_marts = BashOperator(
        task_id="dbt_test_marts",
        bash_command=f"cd {DBT_DIR} && dbt test --select marts --profiles-dir .",
        execution_timeout=timedelta(minutes=10),
    )

    (
        load_source_data
        >> incremental_load_source_to_raw
        >> dbt_run_staging
        >> dbt_test_staging
        >> dbt_run_marts
        >> dbt_test_marts
    )
