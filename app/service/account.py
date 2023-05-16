from app.core.exception import CustomHTTPException
from app.core.model import TokenPayload
from app.core.config import project_config
from app.util.time import get_timestamp_after
from app.util.auth import verify_password, create_access_token

class AccountService:
    def __init__(self):
        return None

    async def login_with_algo(self, email: str, password: str):
        account = await self.get_account_by_email(email)
        if not account:
            raise CustomHTTPException(error_type="unauthorized")
        if not verify_password(password, account.hashed_password):
            raise CustomHTTPException(error_type="unauthorized")
        expire_time = get_timestamp_after(
            minutes=project_config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        confirmation_token = create_access_token(
            TokenPayload(email=email, role=account.role, expire_time=expire_time)
        )
        return confirmation_token
