from core.startup_report.db.startup_report_db_model import StartupReportDbModel
from core.startup_report.db.startup_report_prompt_db_model import (
    StartupReportPromptDbModel,
)


def get_all_startup_reports() -> list[StartupReportDbModel]:
    """Fetch all startup reports from the database."""
    return list(StartupReportDbModel.objects.all().order_by('-created_at'))


def get_startup_report_by_id(report_id: int) -> StartupReportDbModel | None:
    """Fetch a single startup report by ID."""
    try:
        return StartupReportDbModel.objects.get(id=report_id)
    except StartupReportDbModel.DoesNotExist:
        return None


def get_most_recent_prompt() -> StartupReportPromptDbModel | None:
    """Fetch the most recent startup report prompt.

    Returns None if no prompts exist.
    """
    return StartupReportPromptDbModel.objects.order_by('-created_at').first()
