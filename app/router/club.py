from fastapi import APIRouter, Depends, Query
from app.core.constant import SortOrder

from app.core.exception import CustomHTTPException
from app.core.model import HttpResponse, SocketPayload, success_response
from app.core.api import ClubApi
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


@router.get(ClubApi.CLUB_GET)
async def get_one_club(id: str):
    club = await ClubService().get_club({"_id": id})
    if not club:
        raise CustomHTTPException(error_type="club_not_exist")
    return success_response(data=club)


@router.post(ClubApi.CLUB_GETALL, response_model=HttpResponse)
async def get_all_club(
    page_size: int = 20,
    page_number: int = None,
    query: Dict = {},
    orderby: str = "created_at",
    sort: SortOrder = Query(SortOrder.DESC),
):
    result = await ClubService().get_all_club(
        page_size=page_size,
        page_number=page_number,
        query=query,
        orderby=orderby,
        sort=sort.value,
    )
    return success_response(data=result)


@router.post(ClubApi.CLUB_CREATE, response_model=HttpResponse)
async def create_club(
    club_create: Club,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    club, admin_group_id = await ClubService().create_algo_club(club_create)
    member = ClubMembership(
        club_id=club.id,
        user_id=actor,
        role=ClubRole.PRESIDENT,
        group_id=[admin_group_id],
    )
    follower = ClubFollower(club_id=club.id, user_id=actor)
    await ClubService().create_algo_member(member)
    await ClubService().create_algo_follower(follower)
    notification = Notification(
        content=f"Câu lạc bộ {club.name} đã được tạo vào lúc {to_datestring(get_current_timestamp())}",
        to=actor,
        kind=NotiKind.SUCCESS,
    )
    socket_worker.push(
        SocketPayload(
            **get_dict(SocketNotification(client_id=actor, data=notification))
        )
    )
    return success_response(data=club)


@router.put(ClubApi.CLUB_UPDATE, response_model=HttpResponse)
async def update_club(
    club_id: str,
    club_update: Dict,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    if "image" in club_update.keys():
        image_id = await ImageService().save(Image(**club_update["image"]))
        club_update["image"] = image_id
    res = await ClubService().update_algo_club(
        club_id=club_id, actor=actor, data=club_update
    )
    return success_response(data=res)


@router.delete(ClubApi.CLUB_DELETE, response_model=HttpResponse)
async def delete_club(
    club_id: str,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    await ClubService().delete_algo_club(club_id=club_id, actor=actor)
    return success_response()


# ==========================================================


@router.get(ClubApi.GROUP_GET)
async def get_one_group(id: str):
    group = await ClubService().get_group({"_id": id})
    if not group:
        raise CustomHTTPException(error_type="group_not_exist")
    return success_response(data=group)


@router.post(ClubApi.GROUP_GETALL, response_model=HttpResponse)
async def get_all_group(
    page_size: int = 20,
    page_number: int = None,
    query: Dict = {},
    orderby: str = "created_at",
    sort: SortOrder = Query(SortOrder.DESC),
):
    result = await ClubService().get_all_group(
        page_size=page_size,
        page_number=page_number,
        query=query,
        orderby=orderby,
        sort=sort.value,
    )
    return success_response(data=result)


@router.post(ClubApi.GROUP_CREATE, response_model=HttpResponse)
async def create_group(
    group_create: Group,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    group = await ClubService().create_algo_group(group_create)
    socket_worker.push(
        SocketPayload(
            data=f"Câu lạc bộ {group.name} đã được tạo vào lúc {to_datestring(get_current_timestamp())}"
        )
    )
    return success_response(data=group)


@router.put(ClubApi.GROUP_UPDATE, response_model=HttpResponse)
async def update_group(
    group_id: str,
    group_update: Dict,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    res = await ClubService().update_algo_group(
        group_id=group_id, actor=actor, data=group_update
    )
    return success_response(data=res)


@router.delete(ClubApi.GROUP_DELETE, response_model=HttpResponse)
async def delete_group(
    group_id: str,
    group_update: Dict,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    await ClubService().delete_algo_group(group_id=group_id, actor=actor)
    return success_response()


# ==========================================================


@router.get(ClubApi.MEMBER_GET)
async def get_one_member(id: str):
    member = await ClubService().get_member({"_id": id})
    if not member:
        raise CustomHTTPException(error_type="member_not_exist")
    return success_response(data=member)


@router.post(ClubApi.MEMBER_GETALL, response_model=HttpResponse)
async def get_all_member(
    page_size: int = 20,
    page_number: int = None,
    query: Dict = {},
    orderby: str = "created_at",
    sort: SortOrder = Query(SortOrder.DESC),
):
    result = await ClubService().get_all_member(
        page_size=page_size,
        page_number=page_number,
        query=query,
        orderby=orderby,
        sort=sort.value,
    )
    return success_response(data=result)


@router.post(ClubApi.MEMBER_CREATE, response_model=HttpResponse)
async def create_member(
    member_create: ClubMembership,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    member = await ClubService().create_algo_member(member_create, actor)
    return success_response(data=member)


@router.put(ClubApi.MEMBER_UPDATE, response_model=HttpResponse)
async def update_member(
    member_id: str,
    member_update: Dict,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    member = await ClubService().update_algo_member(
        member_id=member_id, actor=actor, data=member_update
    )
    return success_response(
        data={"member_update": member_update, "member_id": member_id}
    )


@router.put(ClubApi.MEMBER_UPDATE_GROUP, response_model=HttpResponse)
async def update_member_group(
    member_id: str,
    group_id: str,
    add: bool = True,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    member = await ClubService().update_algo_member_group(
        member_id=member_id, actor=actor, add=add, group_id=group_id
    )
    return success_response(
        data={"add": add, "group_id": group_id, "member_id": member_id}
    )


@router.delete(ClubApi.MEMBER_DELETE, response_model=HttpResponse)
async def delete_member(
    member_id: str,
    token: str = Depends(oauth2_scheme),
    actor: str = Depends(get_actor_from_request),
):
    await ClubService().delete_algo_member(member_id=member_id, actor=actor)
    return success_response(data=member_id)


# ==========================================================


@router.post(ClubApi.FOLLOW_GETALL, response_model=HttpResponse)
async def get_all_follow(
    page_size: int = 20,
    page_number: int = None,
    query: Dict = {},
    orderby: str = "created_at",
    sort: SortOrder = Query(SortOrder.DESC),
):
    result = await ClubService().get_all_follow(
        page_size=page_size,
        page_number=page_number,
        query=query,
        orderby=orderby,
        sort=sort.value,
    )
    return success_response(data=result)


@router.post(ClubApi.FOLLOW_CREATE, response_model=HttpResponse)
async def create_follow(
    club_id: str,
    token: str = Depends(oauth2_scheme),
    actor=Depends(get_actor_from_request),
):
    follower = ClubFollower(club_id=club_id, user_id=actor)
    follow = await ClubService().create_algo_follower(follower)
    return success_response(data=follow)


@router.delete(ClubApi.FOLLOW_DELETE, response_model=HttpResponse)
async def delete_follow(
    club_id: str,
    token: str = Depends(oauth2_scheme),
    actor=Depends(get_actor_from_request),
):
    follower = ClubFollower(club_id=club_id, user_id=actor)
    await ClubService().delete_algo_follower(follower)
    return success_response()
