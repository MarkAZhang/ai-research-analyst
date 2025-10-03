from core.typed_response_transaction_router import (
    TypedResponseTransactionRouter,
)

from core.default_success_response import DefaultSuccessResponse

router = TypedResponseTransactionRouter()


@router.get("/hello-world")
def hello_world(request):
    return DefaultSuccessResponse()
