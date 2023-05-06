import json
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, TypeVar

from app.core.config import project_config


f_json = open(project_config.RESPONSE_CODE_DIR, encoding="utf8")
response_code = json.load(f_json)
T = TypeVar("T")


class BaseAuditModel(BaseModel):
    created_by: str = "system"
    created_at: int = int(datetime.now().timestamp())
    last_modified_by: str = ""
    last_modified_at: int = None


class HttpResponse(BaseModel):
    status_code = response_code["success"]["code"]
    msg = response_code["success"]["message"]
    data: Optional[T] = None


class TokenPayload(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    expire_time: Optional[int] = None


def custom_response(status_code, message: str, data: T) -> HttpResponse:
    return HttpResponse(status_code=status_code, msg=message, data=data)


def success_response(data=None):
    return HttpResponse(status_code=200, msg="Success", data=data)
