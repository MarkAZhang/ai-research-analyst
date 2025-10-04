from core.startup_report.db.startup_report_db_model import StartupReportDbModel


def create_multiple_startup_reports(names: list[str]) -> list[StartupReportDbModel]:
    """Create multiple startup reports from a list of names using bulk_create."""
    reports_to_create = [
        StartupReportDbModel(
            name=name,
            generation_status='pending',
            read_by_user=False,
            report_text='',
        )
        for name in names
    ]
    return list(StartupReportDbModel.objects.bulk_create(reports_to_create))
