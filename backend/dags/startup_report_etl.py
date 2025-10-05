"""
Airflow DAG for processing startup reports with ETL pipeline.

This DAG performs the following steps:
1. Extract: Fetch the StartupReportDbModel's name and prompt text
2. Transform: Replace {{name}} placeholders in the prompt with the actual name
3. Load: Update the report with the final text and set status to completed/failed
"""
import os
import sys
from datetime import datetime

import django
from airflow.sdk import dag, task, Param

# Add the backend directory to the Python path for Django imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

# Import Django models after setup
from core.startup_report.db.startup_report_db_model import StartupReportDbModel


@dag(
    dag_id='startup_report_etl',
    schedule=None,  # Only triggered manually/programmatically
    start_date=datetime(2025, 1, 1),
    catchup=False,
    params={
        'report_id': Param(
            default=None,
            type=['null', 'integer'],
            description='ID of the StartupReportDbModel to process',
        )
    },
    tags=['startup_report', 'etl'],
)
def startup_report_etl_dag():
    """ETL pipeline for processing startup reports."""

    @task()
    def extract(report_id: int) -> dict:
        """Extract: Fetch the StartupReportDbModel's name and prompt text.

        Args:
            report_id: ID of the report to process

        Returns:
            Dictionary containing report_id, name, and prompt_text
        """
        try:
            report = StartupReportDbModel.objects.select_related('prompt').get(id=report_id)

            if not report.prompt:
                raise ValueError(f"Report {report_id} has no associated prompt")

            return {
                'report_id': report_id,
                'name': report.name,
                'prompt_text': report.prompt.prompt,
            }
        except StartupReportDbModel.DoesNotExist:
            raise ValueError(f"Report with ID {report_id} does not exist")

    @task()
    def transform(extracted_data: dict) -> dict:
        """Transform: Replace {{name}} placeholders in the prompt with the actual name.

        Args:
            extracted_data: Dictionary from extract step containing name and prompt_text

        Returns:
            Dictionary with report_id and final_text (transformed prompt)
        """
        name = extracted_data['name']
        prompt_text = extracted_data['prompt_text']

        # Replace {{name}} with the actual name
        final_text = prompt_text.replace('{{name}}', name)

        return {
            'report_id': extracted_data['report_id'],
            'final_text': final_text,
        }

    @task()
    def load(transformed_data: dict) -> None:
        """Load: Update the report with final text and set status to completed.

        Args:
            transformed_data: Dictionary from transform step containing final_text
        """
        report_id = transformed_data['report_id']
        final_text = transformed_data['final_text']

        report = StartupReportDbModel.objects.get(id=report_id)
        report.report_text = final_text
        report.generation_status = 'completed'
        report.save()

    @task(trigger_rule='one_failed')
    def handle_failure(**context) -> None:
        """Handle DAG failure by setting report status to failed.

        This task only runs when upstream tasks fail.
        """
        report_id = context['params']['report_id']

        try:
            report = StartupReportDbModel.objects.get(id=report_id)
            report.generation_status = 'failed'
            report.save()
        except Exception as e:
            print(f"Error setting failure status for report {report_id}: {e}")

    # Get report_id from params (templated value)
    report_id = "{{ params.report_id }}"  # type: ignore[reportArgumentType]

    # Define the ETL pipeline flow
    extracted_data = extract(report_id)  # type: ignore[reportArgumentType]
    transformed_data = transform(extracted_data)  # type: ignore[reportArgumentType]
    load_task = load(transformed_data)  # type: ignore[reportArgumentType]
    failure_task = handle_failure()

    # Set up dependencies: failure handler runs if extract, transform, or load fails
    [extracted_data, transformed_data, load_task] >> failure_task  # type: ignore[reportOperatorIssue]


# Instantiate the DAG
startup_report_etl = startup_report_etl_dag()
