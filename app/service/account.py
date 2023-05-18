from typing import Dict

from app.core.exception import CustomHTTPException
from app.core.model import TokenPayload
from app.core.config import project_config
from app.core.socket import socket_connection
from app.core.constant import Provider, SortOrder
from app.model.account import Account, AccountCreate, AccountResponse
from app.repo.mongo import get_repo
from app.util.model import get_dict, to_response_dto
from app.util.time import get_current_timestamp, get_timestamp_after, to_datestring
from app.util.auth import (
    get_hashed_password,
    verify_password,
    create_access_token,
)


class AccountService:
    def __init__(self):
        self.account_repo = get_repo(
            Account,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )

    async def get_account(self, query: Dict):
        res = await self.account_repo.get_one(query)
        if not res:
            return None
        id, account = res
        return to_response_dto(id, account, AccountResponse)

    async def get_all(self, **kargs):
        accounts = await self.account_repo.get_all(**kargs)
        res = []
        for doc_id, uv in accounts.items():
            res.append(to_response_dto(doc_id, uv, AccountResponse))
        return res

    async def create_algo_account(
        self, account_create: AccountCreate
    ) -> AccountResponse:
        check_account = await self.get_account({"email": account_create.email})
        if check_account:
            raise CustomHTTPException(error_type="account_already_exist")
        hashed_password = get_hashed_password(account_create.password)
        account = Account(
            hashed_password=hashed_password,
            **get_dict(account_create, allow_none=True),
            active=False,
        )
        inserted_id = await self.account_repo.insert(account)
        await socket_connection.send_data(
            f"{account.email} has been created at {to_datestring(account.created_at)}"
        )
        return to_response_dto(inserted_id, account, AccountResponse)

    async def login_with_firebase(self, id: str, account: Account):
        check_account = await self.account_repo.get_one_by_id(id)
        if not check_account:
            await self.account_repo.insert(account, id)
            await socket_connection.send_data(
                f"{account.email} has been created at {to_datestring(account.created_at)}"
            )
        expire_time = get_timestamp_after(
            minutes=project_config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        confirmation_token = create_access_token(
            TokenPayload(
                username=account.email, role=account.role, expire_time=expire_time
            )
        )
        await socket_connection.send_data(
            f"{account.email} has been joined from {account.provider} at {to_datestring(get_current_timestamp())}"
        )
        return confirmation_token

    async def login_with_algo(self, email: str, password: str):
        check_account = await self.get_account(
            {"email": email, "provider": Provider.SYSTEM}
        )
        if not check_account:
            raise CustomHTTPException(error_type="account_not_exist")
        if not verify_password(password, check_account.hashed_password):
            raise CustomHTTPException(error_type="unauthenticated")
        if not check_account.active:
            raise CustomHTTPException(error_type="account_inactive")
        expire_time = get_timestamp_after(
            minutes=project_config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        confirmation_token = create_access_token(
            TokenPayload(
                username=check_account.id,
                role=check_account.role,
                expire_time=expire_time,
            )
        )
        await socket_connection.send_data(
            f"{check_account.email} has been joined from {check_account.provider} at {to_datestring(get_current_timestamp())}"
        )
        return confirmation_token

    async def active_algo_account(self, id):
        doc_id = await self.account_repo.update_by_id(id, {"active": True})
        await socket_connection.send_data(f"Account {id} has been actived  at {to_datestring(get_current_timestamp())}")
        return doc_id
