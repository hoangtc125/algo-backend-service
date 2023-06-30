from fastapi import APIRouter, Depends, Query
from app.core.constant import SortOrder

from app.core.exception import CustomHTTPException
from app.core.model import HttpResponse, SocketPayload, success_response
from app.core.api import RecruitApi
from app.core.constant import NotiKind
from app.model.image import Image
from app.router.account import oauth2_scheme
from app.service.club import ClubService
from app.model.club import *
from app.model.notification import Notification, SocketNotification
from app.service.image import ImageService
from app.util.auth import get_actor_from_request
from app.util.model import get_dict
from app.util.time import get_current_timestamp, to_datestring
from app.worker.socket import socket_worker
from app.worker.notification import notification_worker

router = APIRouter()


@router.get(RecruitApi.CHECK_PERMISSION)
async def check_permission(
    event_id: str,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    await ClubService().verify_event_owner(event_id=event_id, actor=actor)
    return success_response(data=True)


@router.get(RecruitApi.EVENT_GET)
async def get_one_event(id: str):
    event = await ClubService().get_event({"_id": id})
    if not event:
        raise CustomHTTPException(error_type="event_not_exist")
    return success_response(data=event)


@router.post(RecruitApi.EVENT_GETALL, response_model=HttpResponse)
async def get_all_event(
    page_size: int = 20,
    page_number: int = None,
    query: Dict = {},
    orderby: str = "created_at",
    sort: SortOrder = Query(SortOrder.DESC),
):
    result = await ClubService().get_all_event(
        page_size=page_size,
        page_number=page_number,
        query=query,
        orderby=orderby,
        sort=sort.value,
    )
    return success_response(data=result)


@router.post(RecruitApi.EVENT_CREATE, response_model=HttpResponse)
async def create_event(
    event_create: ClubEvent,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    res = await ClubService().create_algo_event(event_create)
    return success_response(data=res)


@router.put(RecruitApi.EVENT_UPDATE, response_model=HttpResponse)
async def update_event(
    event_id: str,
    event_update: Dict,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    res = await ClubService().update_algo_event(
        event_id=event_id, actor=actor, data=event_update
    )
    return success_response(data=res)


# ==========================================================


@router.get(RecruitApi.ROUND_GET)
async def get_one_round(id: str):
    round = await ClubService().get_round({"_id": id})
    if not round:
        raise CustomHTTPException(error_type="round_not_exist")
    return success_response(data=round)


@router.post(RecruitApi.ROUND_GETALL, response_model=HttpResponse)
async def get_all_round(
    page_size: int = 20,
    page_number: int = None,
    query: Dict = {},
    orderby: str = "created_at",
    sort: SortOrder = Query(SortOrder.DESC),
):
    result = await ClubService().get_all_round(
        page_size=page_size,
        page_number=page_number,
        query=query,
        orderby=orderby,
        sort=sort.value,
    )
    return success_response(data=result)


@router.put(RecruitApi.ROUND_UPDATE, response_model=HttpResponse)
async def update_round(
    event_id: str,
    round_id: str,
    round_update: Dict,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    res = await ClubService().update_algo_round(
        round_id=round_id,
        actor=actor,
        data=round_update,
        event_id=event_id,
    )
    return success_response(data=res)


# ==========================================================


@router.get(RecruitApi.FORM_QUESTION_GET)
async def get_one_form_question(id: str):
    form_question = await ClubService().get_form_question({"_id": id})
    if not form_question:
        raise CustomHTTPException(error_type="unauthorized")
    return success_response(data=form_question)


@router.post(RecruitApi.FORM_QUESTION_GETALL, response_model=HttpResponse)
async def get_all_form_question(
    page_size: int = 20,
    page_number: int = None,
    query: Dict = {},
    orderby: str = "created_at",
    sort: SortOrder = Query(SortOrder.DESC),
):
    result = await ClubService().get_all_form_question(
        page_size=page_size,
        page_number=page_number,
        query=query,
        orderby=orderby,
        sort=sort.value,
    )
    return success_response(data=result)


@router.post(RecruitApi.FORM_QUESTION_CREATE, response_model=HttpResponse)
async def create_form_question(
    club_id: str,
    event_id: str,
    round_id: str,
    form_question_id: str = None,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    clubService = ClubService()
    if not form_question_id:
        res = await clubService.create_form_question(
            FormQuestion(
                club_id=club_id,
                event_id=event_id,
                round_id=round_id,
                sections=[
                    {
                        "id": "b62cd80f-7e84-4373-8f30-42ab09a34f5d",
                        "title": "Mẫu đơn tuyển thành viên",
                        "description": "Mẫu đơn tuyển thành viên cho các Câu lạc bộ học thuật về Công nghệ thông tin",
                        "data": [
                            {
                                "id": "162b384f-b495-4c8a-b2d4-f3462c12147d",
                                "value": "Email cá nhân",
                                "type": "text",
                                "answer": "",
                                "disabled": True,
                                "required": True,
                                "options": [
                                    {
                                        "id": "85000685-e1c5-4447-bb8f-3a541f45be7b",
                                        "value": "",
                                        "to": "",
                                    }
                                ],
                            },
                            {
                                "id": "04ed6a64-26f6-45ad-abd5-bf1c9d425608",
                                "value": "Họ và tên",
                                "type": "text",
                                "answer": "",
                                "disabled": True,
                                "required": True,
                                "options": [
                                    {
                                        "id": "2a92e6d4-2ac8-4379-94d6-36cc75ae4c75",
                                        "value": "",
                                        "to": "",
                                    }
                                ],
                            },
                        ],
                    }
                ],
            )
        )
    else:
        form_question = await clubService.get_form_question({"_id": form_question_id})
        res = await clubService.create_form_question(
            club_id=club_id,
            event_id=event_id,
            round_id=round_id,
            sections=form_question.sections,
        )
    await clubService.update_algo_round(
        event_id=event_id,
        round_id=round_id,
        actor=actor,
        data={"form_question_id": res},
    )
    return success_response(data=res)


@router.put(RecruitApi.FORM_QUESTION_UPDATE, response_model=HttpResponse)
async def update_form_question(
    form_question_id: str,
    form_question_update: Dict,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    res = await ClubService().update_algo_form_question(
        form_question_id=form_question_id, actor=actor, data=form_question_update
    )
    return success_response(data=res)
