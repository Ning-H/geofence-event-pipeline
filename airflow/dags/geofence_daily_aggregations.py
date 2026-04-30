from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


def compact_hourly_raw_partitions(**context):
    logical_date = context["logical_date"]
    print(f"Compact hourly raw ping files for {logical_date:%Y-%m-%d}")


def write_daily_geofence_summaries(**context):
    logical_date = context["logical_date"]
    print(f"Run dwell-time and visit-count aggregations for {logical_date:%Y-%m-%d}")


def freshness_check(**context):
    print("Check latest raw ping object timestamp; alert if no pings arrived in 5 minutes")


with DAG(
    dag_id="geofence_daily_aggregations",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["geofence", "kinesis", "athena"],
) as dag:
    start = EmptyOperator(task_id="start")
    compact = PythonOperator(
        task_id="compact_hourly_raw_partitions",
        python_callable=compact_hourly_raw_partitions,
    )
    aggregate = PythonOperator(
        task_id="write_daily_geofence_summaries",
        python_callable=write_daily_geofence_summaries,
    )
    freshness = PythonOperator(task_id="freshness_check", python_callable=freshness_check)
    done = EmptyOperator(task_id="done")

    start >> freshness >> compact >> aggregate >> done
