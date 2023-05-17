from typing import Tuple
from fastapi import Request

from app.core.exception import CustomHTTPException
from app.core.model import TokenPayload
from app.core.api import ALLOW_ALL, WHITE_LIST_IP, API_PERMISSION
from app.core.auth import authenticate_internal_request
from app.util.auth import get_token_payload


def authentication(request: Request):
    request_username = "unknown"
    request_role = "unknown"
    request_user = TokenPayload(username=request_username, role=request_role)
    try:
        access_token = request.headers["authorization"]
        if "Bearer" not in access_token:
            return request_user
        token = access_token.split(" ")[1]
        request_user = get_token_payload(token)
        request_role = request_user.role
        request_username = request_user.username
    except KeyError as e:
        pass
    except CustomHTTPException as ex:
        raise ex
    request_username_header: Tuple[bytes] = ("x-request-user".encode(), request_username.encode())
    request_role_header: Tuple[bytes] = ("x-request-role".encode(), request_role.encode())
    request.headers.__dict__["_list"].append(request_username_header)
    request.headers.__dict__["_list"].append(request_role_header)
    return request_user


def authorization(path, request_role=None, request_host=None, request=None):
    if (
        (request_host in WHITE_LIST_IP)
        and (path in WHITE_LIST_IP[request_host])
        and authenticate_internal_request(request)
    ):
        return
    if path not in API_PERMISSION:
        return
    accepted_role = API_PERMISSION[path]
    if accepted_role == ALLOW_ALL or request_role in accepted_role:
        return
    raise CustomHTTPException(error_type="unauthorized")
