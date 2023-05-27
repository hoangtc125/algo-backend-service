from typing import Dict
from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
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
from app.service.detect import (
    detect_code_from_base64,
    detect_text_from_base64,
    file_to_base64,
    make_card_hust,
)
from app.service.notification import NotificationService
from app.model.account import AccountCreate, Account, PasswordUpdate
from app.model.notification import Notification, SocketNotification
from app.util.auth import get_actor_from_request
from app.util.mail import (
    make_mail_active_account,
    make_mail_reset_password,
    make_mail_verify_account,
)
from app.util.model import get_dict
from app.util.time import get_current_timestamp, to_datestring
from app.util.mail import Email
from app.worker.socket import socket_worker
from app.worker.mail import mail_worker
from app.worker.notification import notification_worker

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
    account = await AccountService().create_algo_account(account_create)
    token = AccountService().make_token(account.id)
    mail_worker.push(
        Email(
            receiver_email=account.email,
            subject="Kích hoạt tài khoản ALGO",
            content=make_mail_active_account(
                f"http://{project_config.HOST}:{project_config.ALGO_PORT}{AccountApi.ACTIVE}?token={token}"
            ),
        )
    )
    socket_worker.push(
        SocketPayload(
            data=f"Email active account be sent to {account.email} at {to_datestring(get_current_timestamp())}"
        )
    )
    return success_response(data=token)


@router.get(AccountApi.ABOUT_ME)
async def about_me(
    token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)
):
    account = await AccountService().get_account({"_id": actor})
    if not account:
        raise CustomHTTPException(error_type="account_not_exist")
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
async def active(token: str):
    await AccountService().active_algo_account(token)
    return RedirectResponse(
        url=f"http://{project_config.HOST}:{project_config.FRONTEND_PORT}/login"
    )


@router.post(AccountApi.NOTIFICATION, response_model=HttpResponse)
async def get_notification(
    page_size: int = 5,
    page_number: int = 0,
    query: Dict = {},
    orderby: str = "created_at",
    sort: SortOrder = Query(SortOrder.DESC),
    token: str = Depends(oauth2_scheme),
):
    result = await NotificationService().get_all(
        page_size=page_size,
        page_number=page_number,
        query=query,
        orderby=orderby,
        sort=sort.value,
    )
    return success_response(data=result)


@router.get(AccountApi.RESET_PASSWORD, response_model=HttpResponse)
async def send_mail_reset(email: str):
    account = await AccountService().get_account(
        {"email": email, "provider": Provider.SYSTEM}
    )
    if not account:
        raise CustomHTTPException(error_type="account_not_exist")
    token = AccountService().make_token(account.id)
    mail_worker.push(
        Email(
            receiver_email=email,
            subject="Thông báo đặt lại mật khẩu",
            content=make_mail_reset_password(
                f"http://{project_config.HOST}:{project_config.FRONTEND_PORT}/reset-password?token={token}"
            ),
        )
    )
    return success_response()


@router.post(AccountApi.RESET_PASSWORD, response_model=HttpResponse)
async def reset_password(passwordUpdate: PasswordUpdate):
    res = await AccountService().reset_password(passwordUpdate)
    return success_response(data=res)


@router.get(AccountApi.VERIFY, response_model=HttpResponse)
async def verify(token: str):
    await AccountService().verify_account(token)
    return success_response()


@router.post(AccountApi.VERIFY, response_model=HttpResponse)
async def request_verify(
    image_bytes: str = None,
    token: str = Depends(oauth2_scheme),
    actor=Depends(get_actor_from_request),
):
    file_path = r"/home/hoangtc125/Downloads/20194060-Trần Công Hoàng.jpg"
    image_base64 = file_to_base64(file_path)
    info_list = detect_text_from_base64(image_base64)
    code_list = detect_code_from_base64(image_base64)
    card = make_card_hust(info_list)
    if card.number not in code_list:
        raise CustomHTTPException(error_type="detect_barcode_failure")
    await AccountService().account_repo.update_by_id(
        actor, {"verify": {"status": False, "type": "HUST", "detail": card.__dict__}}
    )
    token = AccountService().make_token(actor)
    mail_worker.push(
        Email(
            receiver_email=card.email,
            subject="Yêu cầu xác thực tài khoản",
            content=make_mail_verify_account(
                card.__dict__,
                f"http://{project_config.HOST}:{project_config.ALGO_PORT}{AccountApi.VERIFY}?token={token}",
            ),
        )
    )
    notification = Notification(
        content=f"A link to verify your account has been sent to {card.email}", to=actor
    )
    socket_worker.push(
        SocketPayload(
            **get_dict(SocketNotification(client_id=actor, data=notification))
        )
    )
    notification_worker.create(notification)
    return success_response()
