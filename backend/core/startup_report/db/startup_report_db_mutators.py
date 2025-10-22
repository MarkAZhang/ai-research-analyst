from core.airflow_client import airflow_client
from core.startup_report.db.startup_report_db_model import StartupReportDbModel
from core.startup_report.db.startup_report_prompt_db_model import (
    StartupReportPromptDbModel,
)


def create_multiple_startup_reports(names: list[str]) -> list[StartupReportDbModel]:
    """Create multiple startup reports from a list of names using bulk_create.

    After creating the reports, triggers an Airflow DAG for each report.

    Raises:
        ValueError: If no prompt exists in the database.
    """
    # Get the most recent prompt to link to the new reports
    most_recent_prompt = StartupReportPromptDbModel.objects.order_by('-created_at').first()

    if not most_recent_prompt:
        raise ValueError(
            'No prompt found. Please create a prompt before creating reports.'
        )

    reports_to_create = [
        StartupReportDbModel(
            name=name,
            generation_status='pending',
            read_by_user=False,
            report_text='',
            prompt=most_recent_prompt,
        )
        for name in names
    ]
    created_reports = list(StartupReportDbModel.objects.bulk_create(reports_to_create))

    # Trigger Airflow DAG for each created report
    for report in created_reports:
        # Update status to 'started' before triggering the DAG
        report.generation_status = 'started'
        report.save()

        # Trigger the DAG with the report ID
        airflow_client.trigger_dag(
            dag_id='startup_report_etl',
            conf={'report_id': report.id}  # type: ignore[reportAttributeAccessIssue]
        )

    return created_reports


def delete_multiple_startup_reports(report_ids: list[int]) -> int:
    """Delete multiple startup reports by their IDs.

    Returns the number of reports deleted.
    """
    deleted_count, _ = StartupReportDbModel.objects.filter(id__in=report_ids).delete()
    return deleted_count


def create_startup_report_prompt(prompt_text: str) -> StartupReportPromptDbModel:
    """Create a new startup report prompt.

    This creates a new prompt rather than updating an existing one,
    preserving the history of all prompts.
    """
    return StartupReportPromptDbModel.objects.create(prompt=prompt_text)
