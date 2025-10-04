from ninja.errors import HttpError

from core.base_pydantic_models import BaseRequestModel, BaseResponseModel
from core.default_success_response import DefaultSuccessResponse
from core.startup_report.db.startup_report_db_model import StartupReportDbModel
from core.startup_report.db.startup_report_db_mutators import (
    create_multiple_startup_reports,
)
from core.startup_report.db.startup_report_db_queries import get_all_startup_reports
from core.typed_response_transaction_router import TypedResponseTransactionRouter

router = TypedResponseTransactionRouter()


class StartupReportResponse(BaseResponseModel):
    id: int
    name: str
    created_at: str
    read_by_user: bool
    generation_status: str
    report_text: str


class GetStartupReportsResponse(BaseResponseModel):
    reports: list[StartupReportResponse]


class CreateStartupReportsRequest(BaseRequestModel):
    names: list[str]


@router.get('/startup-report')
def get_startup_reports(request) -> GetStartupReportsResponse:
    """Fetch all available startup reports."""
    reports = get_all_startup_reports()

    return GetStartupReportsResponse(
        reports=[
            StartupReportResponse(
                id=report.id,  # type: ignore[reportAttributeAccessIssue]
                name=report.name,
                created_at=report.created_at.isoformat(),
                read_by_user=report.read_by_user,
                generation_status=report.generation_status,
                report_text=report.report_text,
            )
            for report in reports
        ]
    )


@router.post('/startup-report/create')
def create_startup_reports(
    request, payload: CreateStartupReportsRequest
) -> DefaultSuccessResponse:
    """Create startup reports for each name in the provided list."""
    if not payload.names:
        raise HttpError(400, 'Names list cannot be empty')

    create_multiple_startup_reports(payload.names)
    return DefaultSuccessResponse()
