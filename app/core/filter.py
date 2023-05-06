from fastapi import Request
from firebase_admin.auth import verify_id_token
from firebase_admin._auth_utils import InvalidIdTokenError

from app.core.exception import CustomHTTPException
from app.core.model import TokenPayload


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


def authorization():
    pass

if __name__ == "__main__":
    decode_token = verify_id_token("12123")