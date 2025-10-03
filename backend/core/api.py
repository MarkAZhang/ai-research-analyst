from ninja import Router

from core.default_success_response import DefaultSuccessResponse

router = Router()


@router.get('/hello-world', response=DefaultSuccessResponse)
def hello_world(request):
    return DefaultSuccessResponse()
