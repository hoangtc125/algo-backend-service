import datetime
from typing import Optional, TypeVar

from fastapi import Response
import json
import time
import traceback
import threading

from jose import JWTError, jwt
from pydantic import BaseModel
from requests import post, get
from datetime import timezone
from fastapi import Request
from passlib.hash import bcrypt
from app.core.config import project_config

T = TypeVar("T")


def get_dict(object: T, allow_none=False):
    res = {}
    data = object if type(object) is dict else object.__dict__
    for key, value in data.items():
        if value is None and allow_none == False:
            continue
        if isinstance(value, BaseModel):
            res[key] = get_dict(value)
        elif type(value) is list:
            res[key] = []
            for item in value:
                res[key].append(
                    get_dict(item, allow_none) if isinstance(item, BaseModel) else item
                )
        elif type(value) is not dict:
            res[key] = value
        elif len(value.keys()) == 0:
            continue
        else:
            res[key] = get_dict(value, allow_none)
    return res


class TokenPayload(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    expire_time: Optional[int] = None


class InternalAuth:
    CURRENT_TOKEN = None
    SESSION_EXPIRED_AFTER = 5
    TOKEN_REFRESH_INTERVAL = 3

    @staticmethod
    def post(url, data=None, json=None, **kwargs):
        if not kwargs.get("headers"):
            kwargs["headers"] = {}
        kwargs["headers"]["internal-auth"] = InternalAuth.CURRENT_TOKEN
        return post(url, data=data, json=json, **kwargs)

    @staticmethod
    def get(url, data=None, params=None, **kwargs):
        if not kwargs.get("headers"):
            kwargs["headers"] = {}
        kwargs["headers"]["internal-auth"] = InternalAuth.CURRENT_TOKEN
        return get(url, params=params, **kwargs)


def create_token_generator():
    def __generate_token():
        while True:
            token_payload = TokenPayload(
                username=project_config.SERVICE_NAME,
                expire_time=datetime.datetime.now(tz=timezone.utc).timestamp()
                + InternalAuth.SESSION_EXPIRED_AFTER,
            )
            try:
                InternalAuth.CURRENT_TOKEN = create_access_token(token_payload)
            except:
                traceback.print_exc()
            time.sleep(InternalAuth.TOKEN_REFRESH_INTERVAL)

    worker_thread = threading.Thread(target=__generate_token, args=())
    worker_thread.daemon = True
    worker_thread.start()


def authenticate_internal_request(request: Request):
    if request.url.path in [
        "/docs",
        "/favicon.ico",
        "/openapi.json",
    ]:
        return True
    try:
        access_token = request.headers["internal-auth"]
        get_token_payload(access_token)
    except:
        return False
    return True


async def add_internal_auth_middleware(request: Request, call_next):
    if not authenticate_internal_request(request):
        return Response(
            status_code=400,
            headers={"access-control-allow-origin": "*"},
            content=json.dumps({"status_code": 61200, "msg": "Internal auth failed"}),
        )
    response = await call_next(request)
    return response


def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)


def get_hashed_password(password):
    return bcrypt.hash(password)


def create_access_token(data: TokenPayload):
    to_encode = get_dict(data)
    token = jwt.encode(
        to_encode,
        project_config.SECRET_KEY,
        algorithm=project_config.SECURITY_ALGORITHM,
    )
    return token


def get_token_payload(token: str):
    try:
        payload_data = jwt.decode(
            token,
            project_config.SECRET_KEY,
            algorithms=[project_config.SECURITY_ALGORITHM],
        )
        token_payload = TokenPayload(**payload_data)
        username: str = token_payload.username
        expire = token_payload.expire_time
        if username is None:
            raise Exception("Authen Failed")
        if expire < datetime.datetime.now(tz=timezone.utc).timestamp():
            raise Exception("Authen Failed")
    except JWTError:
        raise Exception("Authen Failed")
    return token_payload
