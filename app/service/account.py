from app.core.exception import CustomHTTPException
from app.core.model import TokenPayload
from app.core.config import project_config
from app.core.constant import Provider
from app.model.account import Account, AccountCreate, AccountResponse
from app.repo.mongo import get_repo
from app.util.model import get_dict, to_response_dto
from app.util.time import get_timestamp_after
from app.util.auth import get_hashed_password, verify_password, create_access_token
from app.util.mongo import make_body


class AccountService:
    def __init__(self):
        self.account_repo = get_repo(
            Account,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )

    async def get_account(self, email: str):
        res = await self.account_repo.get_one(make_body({"email": email}))
        if not res:
            return None
        id, account = res
        return to_response_dto(id, account, AccountResponse)
    
    async def get_all(self):
        accounts = await self.account_repo.get_all()
        res = []
        for doc_id, uv in accounts.items():
            res.append(to_response_dto(doc_id, uv, AccountResponse))
        return res

    async def create_algo_account(self, account_create: AccountCreate):
        check_account = await self.get_account(account_create.email)
        if check_account:
            raise CustomHTTPException(error_type="account_already_exist")
        if account_create.provider == Provider.ALGO:
            hashed_password = get_hashed_password(account_create.password)
        account = Account(
            hashed_password=hashed_password, **get_dict(account_create, allow_none=True)
        )
        print(account, account.email)
        inserted_id = await self.account_repo.insert(account, account.email)
        return to_response_dto(inserted_id, account, AccountResponse)

    async def login_with_algo(self, email: str, password: str):
        check_account = await self.get_account(email)
        if not check_account:
            raise CustomHTTPException(error_type="unauthorized")
        if not verify_password(password, check_account.hashed_password):
            raise CustomHTTPException(error_type="unauthorized")
        expire_time = get_timestamp_after(
            minutes=project_config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        confirmation_token = create_access_token(
            TokenPayload(email=email, role=check_account.role, expire_time=expire_time)
        )
        return confirmation_token
