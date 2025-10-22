"""
Airflow DAG for processing startup reports with ETL pipeline.

This DAG performs the following steps:
1. Extract: Fetch the StartupReport's name and prompt text from SQLite database
2. Transform: Hydrate prompt with name, send to OpenAI API, and receive LLM response
3. Load: Update the report with the final text and set status to completed/failed
"""

from datetime import datetime

from airflow.sdk import dag, Param

from common import load_environment
from tasks.extract import extract
from tasks.transform import transform
from tasks.load import load

# Load environment variables from .env file in airflow directory
load_environment()


@dag(
    dag_id="startup_report_etl",
    schedule=None,  # Only triggered manually/programmatically
    start_date=datetime(2025, 1, 1),
    catchup=False,
    params={
        "report_id": Param(
            default=None,
            type=["null", "integer"],
            description="ID of the StartupReportDbModel to process",
        )
    },
    tags=["startup_report", "etl"],
)
def startup_report_etl_dag():
    """ETL pipeline for processing startup reports."""

    # Get report_id from params (templated value)
    report_id = "{{ params.report_id }}"  # type: ignore[reportArgumentType]

    # Define the ETL pipeline flow
    extracted_data = extract(report_id)  # type: ignore[reportArgumentType]
    transformed_data = transform(extracted_data)  # type: ignore[reportArgumentType]
    load(transformed_data)  # type: ignore[reportArgumentType]


# Instantiate the DAG
startup_report_etl = startup_report_etl_dag()
