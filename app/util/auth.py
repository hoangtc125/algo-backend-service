from jose import JWTError, jwt

from app.core.exception import CustomHTTPException
from app.core.config import project_config
from app.core.model import TokenPayload
from app.core.model import ConfirmationToken
from app.util.time import get_current_timestamp
from app.util.model import get_dict
from passlib.hash import bcrypt


def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)


def get_hashed_password(password):
    return bcrypt.hash(password)


def create_access_token(data: TokenPayload) -> ConfirmationToken:
    to_encode = get_dict(data)
    token = jwt.encode(
        to_encode,
        project_config.SECRET_KEY,
        algorithm=project_config.SECURITY_ALGORITHM,
    )
    return ConfirmationToken(
        token=token, created_at=get_current_timestamp(), expires_at=data.expire_time
    )


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
            raise CustomHTTPException(error_type="unauthorized")
        if expire < get_current_timestamp():
            raise CustomHTTPException(error_type="expired_token")
    except JWTError:
        raise CustomHTTPException(error_type="unauthorized")
    return token_payload
