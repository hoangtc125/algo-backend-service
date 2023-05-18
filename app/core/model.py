import json
from pydantic import BaseModel, root_validator
from datetime import datetime
from typing import Optional, TypeVar

from app.core.config import project_config
from app.core.constant import Provider


f_json = open(project_config.RESPONSE_CODE_DIR, encoding="utf-8")
response_code = json.load(f_json)
T = TypeVar("T")


class BaseAuditModel(BaseModel):
    created_by: str = Provider.SYSTEM
    created_at: int = None
    last_modified_by: str = ""
    last_modified_at: int = None

    @root_validator
    def timestamp(cls, values):
        if values["created_at"] is None:
            values["created_at"] = int(datetime.now().timestamp())
        return values


class HttpResponse(BaseModel):
    status_code = response_code["success"]["code"]
    msg = response_code["success"]["message"]
    data: Optional[T] = None


class TokenPayload(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    expire_time: Optional[int] = None


class ConfirmationToken(BaseModel):
    token_type: str = "Bearer"
    token: str
    created_at: int
    expires_at: int


def custom_response(status_code, message: str, data: T) -> HttpResponse:
    return HttpResponse(status_code=status_code, msg=message, data=data)


def success_response(data=None):
    return HttpResponse(status_code=200, msg="Success", data=data)
