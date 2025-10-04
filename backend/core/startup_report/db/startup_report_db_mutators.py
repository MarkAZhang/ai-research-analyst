from core.startup_report.db.startup_report_db_model import StartupReportDbModel


def create_startup_report(name: str) -> StartupReportDbModel:
    """Create a new startup report with the given name."""
    return StartupReportDbModel.objects.create(
        name=name,
        generation_status='pending',
        read_by_user=False,
        report_text='',
    )


def create_multiple_startup_reports(names: list[str]) -> list[StartupReportDbModel]:
    """Create multiple startup reports from a list of names."""
    reports = []
    for name in names:
        report = create_startup_report(name)
        reports.append(report)
    return reports
