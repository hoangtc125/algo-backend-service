from typing import Dict
from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from firebase_admin.auth import verify_id_token
from firebase_admin._auth_utils import InvalidIdTokenError

from app.core.constant import Provider, SortOrder
from app.core.exception import CustomHTTPException
from app.core.model import HttpResponse, SocketPayload, success_response
from app.core.oauth2 import CustomOAuth2PasswordBearer
from app.core.api import AccountApi, get_permissions
from app.core.config import project_config
from app.core.log import logger
from app.service.account import AccountService
from app.model.account import AccountCreate, Account
from app.util.auth import get_actor_from_request
from app.util.mail import make_mail_active_account
from app.util.time import get_current_timestamp, to_datestring
from app.util.mail import Email
from app.worker.socket import socket_worker
from app.worker.mail import mail_worker

router = APIRouter()
oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl=AccountApi.LOGIN)


@router.post(AccountApi.LOGIN)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    result = await AccountService().login_with_algo(
        form_data.username, form_data.password
    )
    return {"token_type": result.token_type, "access_token": result.token}


@router.post(AccountApi.LOGIN_FIREBASE)
async def login_firebase(firebase_token: str):
    try:
        decode_token = verify_id_token(firebase_token)
    except InvalidIdTokenError:
        raise CustomHTTPException(error_type="unauthenticated")
    logger.log(decode_token)
    account = Account(
        created_by=Provider.FIREBASE,
        name=decode_token.get("name", f"USER-{get_current_timestamp()}"),
        photo_url=decode_token.get("picture"),
        email=decode_token["email"],
        provider=decode_token["firebase"]["sign_in_provider"],
        active=True,
    )
    result = await AccountService().login_with_firebase(
        decode_token["user_id"], account
    )
    return {"token_type": result.token_type, "access_token": result.token}


@router.post(AccountApi.REGISTER, response_model=HttpResponse)
async def register(account_create: AccountCreate):
    result = await AccountService().create_algo_account(account_create)
    mail_worker.push(
        Email(
            receiver_email=result.email,
            subject="Kích hoạt tài khoản ALGO",
            content=make_mail_active_account(
                f"http://0.0.0.0:{project_config.ALGO_PORT}/account/active?id={result.id}"
            ),
        )
    )
    socket_worker.push(
        SocketPayload(
            data=f"Email active account be sent to {result.email} at {to_datestring(get_current_timestamp())}"
        )
    )
    return success_response(data=result)


@router.get(AccountApi.ABOUT_ME)
async def about_me(
    token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)
):
    account = await AccountService().get_account({"_id": actor})
    lst_api_permissions = get_permissions(account.role)
    result = {"account": account, "api_permissions": lst_api_permissions}
    return success_response(data=result)


@router.get(AccountApi.GET, response_model=HttpResponse)
async def get(
    id: str,
    token: str = Depends(oauth2_scheme),
):
    result = await AccountService().get_account({"_id": id})
    if not result:
        raise CustomHTTPException(error_type="account_not_exist")
    return success_response(data=result)


@router.post(AccountApi.GET_ALL, response_model=HttpResponse)
async def get_all(
    page_size: int = 20,
    page_number: int = None,
    query: Dict = {},
    orderby: str = "created_at",
    sort: SortOrder = Query(SortOrder.DESC),
    token: str = Depends(oauth2_scheme),
):
    result = await AccountService().get_all(
        page_size=page_size,
        page_number=page_number,
        query=query,
        orderby=orderby,
        sort=sort.value,
    )
    return success_response(data=result)


@router.get(AccountApi.ACTIVE, response_model=HttpResponse)
async def active(id: str):
    result = await AccountService().active_algo_account(id)
    return success_response(data=result)
