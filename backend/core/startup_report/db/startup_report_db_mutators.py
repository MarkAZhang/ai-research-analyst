from core.startup_report.db.startup_report_db_model import StartupReportDbModel
from core.startup_report.db.startup_report_prompt_db_model import (
    StartupReportPromptDbModel,
)


def create_multiple_startup_reports(names: list[str]) -> list[StartupReportDbModel]:
    """Create multiple startup reports from a list of names using bulk_create.

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
    return list(StartupReportDbModel.objects.bulk_create(reports_to_create))


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
