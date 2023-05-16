from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.core.model import HttpResponse, success_response
from app.core.oauth2 import CustomOAuth2PasswordBearer
from app.core.api import AccountApi, get_permissions
from app.service.account import AccountService

router = APIRouter()
oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl=AccountApi.LOGIN)


def get_actor_from_request(request: Request):
    try:
        return request._headers["x-request-user"]
    except:
        return None


def get_role_from_request(request: Request):
    try:
        return request._headers["x-request-role"]
    except:
        return None


@router.post(AccountApi.LOGIN)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    result = await AccountService().login_with_algo(
        form_data.username, form_data.password
    )
    return {"token_type": result.token_type, "access_token": result.token}


@router.post(AccountApi.LOGIN_FIREBASE)
async def login_firebase():
    pass


@router.post(AccountApi.REGISTER, response_model=HttpResponse)
async def register(
    account_create: AccountCreate,
    token: str = Depends(oauth2_scheme),
    actor=Depends(get_actor_from_request),
):
    result = await AccountService().create_one_account(account_create, actor)
    return success_response(data=result)


@router.get(AccountApi.ABOUT_ME)
async def about_me(
    token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)
):
    account = await AccountService().get_account_by_username(actor)
    lst_api_permissions = get_permissions(account.role)
    result = {"account": account, "api_permissions": lst_api_permissions}
    return success_response(data=result)
