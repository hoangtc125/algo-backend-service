from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from firebase_admin.auth import verify_id_token
from firebase_admin._auth_utils import InvalidIdTokenError

from app.core.constant import Provider
from app.core.exception import CustomHTTPException
from app.core.model import HttpResponse, success_response
from app.core.oauth2 import CustomOAuth2PasswordBearer
from app.core.api import AccountApi, get_permissions
from app.core.config import project_config
from app.service.account import AccountService
from app.model.account import AccountCreate, Account
from app.service.mail import make_and_send_mail_active_account
from app.util.auth import get_actor_from_request
from app.core.socket import socket_connection

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
    account = Account(
        created_by=Provider.FIREBASE,
        name=decode_token["name"],
        photo_url=decode_token["picture"],
        email=decode_token["email"],
        provider=decode_token["firebase"]["sign_in_provider"],
        active=True,
    )
    result = await AccountService().login_with_firebase(
        decode_token["user_id"], account
    )
    return {"token_type": result.token_type, "access_token": result.token}


@router.post(AccountApi.REGISTER, response_model=HttpResponse)
async def register(account_create: AccountCreate, background_tasks: BackgroundTasks):
    result = await AccountService().create_algo_account(account_create)
    background_tasks.add_task(
        make_and_send_mail_active_account,
        result.email,
        f"http://0.0.0.0:{project_config.ALGO_PORT}/account/active?id={result.id}",
    )
    await socket_connection.send_data(f"Email active account be sent to {result.email}")
    return success_response(data=result)


@router.get(AccountApi.ABOUT_ME)
async def about_me(
    token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)
):
    account = await AccountService().get_account(actor)
    lst_api_permissions = get_permissions(account.role)
    result = {"account": account, "api_permissions": lst_api_permissions}
    return success_response(data=result)


@router.get(AccountApi.GET, response_model=HttpResponse)
async def get(
    email: str,
    token: str = Depends(oauth2_scheme),
):
    result = await AccountService().get_account(email)
    if not result:
        raise CustomHTTPException(error_type="account_not_exist")
    return success_response(data=result)


@router.get(AccountApi.GET_ALL, response_model=HttpResponse)
async def get(
    token: str = Depends(oauth2_scheme),
):
    result = await AccountService().get_all()
    return success_response(data=result)


@router.get(AccountApi.ACTIVE, response_model=HttpResponse)
async def active(id: str):
    result = await AccountService().active_algo_account(id)
    return success_response(data=result)
