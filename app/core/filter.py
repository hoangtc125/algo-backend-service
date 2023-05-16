from fastapi import Request
from firebase_admin.auth import verify_id_token
from firebase_admin._auth_utils import InvalidIdTokenError

from app.core.exception import CustomHTTPException
from app.core.model import TokenPayload
from app.core.api import ALLOW_ALL, WHITE_LIST_IP, API_PERMISSION
from app.core.auth import authenticate_internal_request


def authentication(request: Request):
    request_username = "unknown"
    request_role = "unknown"
    request_user = TokenPayload(username=request_username, role=request_role)
    try:
        access_token = request.headers["authorization"]
        if "Bearer" not in access_token:
            return request_user
        token = access_token.split(" ")[1]
        decode_token = verify_id_token(token)

    except KeyError:
        pass
    except InvalidIdTokenError:
        raise CustomHTTPException(error_type="unauthenticated")
    except Exception:
        raise CustomHTTPException(error_type="system_error")


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
    raise CustomHTTPException(error_type="permission_denied")


if __name__ == "__main__":
    decode_token = verify_id_token("12123")
