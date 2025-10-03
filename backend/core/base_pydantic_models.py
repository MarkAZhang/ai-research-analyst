from pydantic import BaseModel, ConfigDict


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
