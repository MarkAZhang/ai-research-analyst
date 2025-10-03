from core.base_pydantic_models import BaseResponseModel


class DefaultSuccessResponse(BaseResponseModel):
    success: bool = True
