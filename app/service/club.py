import traceback
from typing import Dict

from app.core.exception import CustomHTTPException
from app.core.model import SocketPayload
from app.core.constant import NotiKind
from app.core.config import project_config
from app.model.notification import Notification, SocketNotification
from app.model.club import *
from app.repo.mongo import get_repo
from app.util.model import get_dict, to_response_dto
from app.util.time import get_current_timestamp, to_datestring
from app.worker.socket import socket_worker
from app.worker.notification import notification_worker


class ClubService:
    def __init__(self):
        self.club_repo = get_repo(
            Club,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
        self.group_repo = get_repo(
            Group,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
        self.member_repo = get_repo(
            ClubMembership,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
        self.follow_repo = get_repo(
            ClubFollower,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )

    async def verify_club_president(self, club_id: str, actor: str):
        club = await self.get_club({"_id": club_id})
        if not club:
            raise CustomHTTPException("club_not_exist")
        member = await self.get_member(
            {
                "club_id": club_id,
                "user_id": actor,
            }
        )
        if not member:
            raise CustomHTTPException("member_not_exist")
        if member.role != ClubRole.PRESIDENT:
            raise CustomHTTPException("member_invalid_action")
        return (club, member)

    async def verify_club_admin_group(self, club_id: str, actor: str):
        club = await self.get_club({"_id": club_id})
        if not club:
            raise CustomHTTPException("club_not_exist")
        member = await self.get_member(
            {
                "club_id": club_id,
                "user_id": actor,
            }
        )
        if not member:
            raise CustomHTTPException("member_not_exist")
        group = await self.get_group(
            {"club_id": club_id, "_id": {"$in": member.group_id}, "is_remove": False}
        )
        if not group:
            raise CustomHTTPException("member_invalid_action")
        return (club, member)

    async def get_club(self, query: Dict):
        res = await self.club_repo.get_one(query)
        if not res:
            return None
        id, club = res
        return to_response_dto(id, club, ClubResponse)

    async def get_all_club(self, **kargs):
        clubs = await self.club_repo.get_all(**kargs)
        res = []
        for doc_id, uv in clubs.items():
            res.append(to_response_dto(doc_id, uv, ClubResponse))
        return res

    async def create_algo_club(self, club: Club) -> ClubResponse:
        inserted_id = await self.club_repo.insert(club)
        for i in range(len(GroupDefault)):
            GroupDefault[i]["obj"].club_id = inserted_id
        groups_id = await self.group_repo.insert_many(GroupDefault)
        return (to_response_dto(inserted_id, club, ClubResponse), str(groups_id[0]))

    async def update_algo_club(self, club_id: str, actor: str, data: Dict):
        club, _ = await self.verify_club_admin_group(club_id=club_id, actor=actor)
        doc_id = await self.club_repo.update_by_id(club_id, data)
        notification = Notification(
            content=f"Câu lạc bộ {club.name} đã được cập nhật vào lúc {to_datestring(get_current_timestamp())}",
            to=actor,
            kind=NotiKind.SUCCESS,
        )
        socket_worker.push(
            SocketPayload(
                **get_dict(SocketNotification(client_id=actor, data=notification))
            )
        )
        return doc_id

    async def delete_algo_club(self, club_id: str, actor: str):
        club, _ = await self.verify_club_president(club_id=club_id, actor=actor)
        await self.club_repo.delete({"_id": club_id})
        await self.member_repo.delete_many({"club_id": club_id})
        await self.group_repo.delete_many({"club_id": club_id})
        await self.follow_repo.delete_many({"club_id": club_id})
        notification = Notification(
            content=f"Câu lạc bộ {club.name} đã được xóa vào lúc {to_datestring(get_current_timestamp())}",
            to=actor,
            kind=NotiKind.SUCCESS,
        )
        socket_worker.push(
            SocketPayload(
                **get_dict(SocketNotification(client_id=actor, data=notification))
            )
        )

    # ========================================================

    async def get_group(self, query: Dict):
        res = await self.group_repo.get_one(query)
        if not res:
            return None
        id, group = res
        return to_response_dto(id, group, GroupResponse)

    async def get_all_group(self, **kargs):
        groups = await self.group_repo.get_all(**kargs)
        res = []
        for doc_id, uv in groups.items():
            res.append(to_response_dto(doc_id, uv, GroupResponse))
        return res

    async def create_algo_group(self, group: Group) -> GroupResponse:
        inserted_id = await self.group_repo.insert(group)
        return to_response_dto(inserted_id, group, GroupResponse)

    async def update_algo_group(self, group_id: str, actor: str, data: Dict):
        group = await self.get_group({"_id": group_id})
        if not group:
            raise CustomHTTPException("group_not_exist")
        await self.verify_club_admin_group(club_id=group.club_id, actor=actor)
        doc_id = await self.group_repo.update_by_id(group_id, data)
        notification = Notification(
            content=f"{group.name} đã được cập nhật vào lúc {to_datestring(get_current_timestamp())}",
            to=actor,
            kind=NotiKind.SUCCESS,
        )
        socket_worker.push(
            SocketPayload(
                **get_dict(SocketNotification(client_id=actor, data=notification))
            )
        )
        return doc_id

    async def delete_algo_group(self, group_id: str, actor: str):
        group = await self.get_group({"_id": group_id})
        if not group:
            raise CustomHTTPException("group_not_exist")
        if group.is_remove:
            await self.verify_club_admin_group(club_id=group.club_id, actor=actor)
        else:
            raise CustomHTTPException("member_invalid_action")
        await self.group_repo.delete({"_id": group_id})
        notification = Notification(
            content=f"{group.name} đã được xóa vào lúc {to_datestring(get_current_timestamp())}",
            to=actor,
            kind=NotiKind.SUCCESS,
        )
        socket_worker.push(
            SocketPayload(
                **get_dict(SocketNotification(client_id=actor, data=notification))
            )
        )

    # ========================================================

    async def get_member(self, query: Dict):
        res = await self.member_repo.get_one(query)
        if not res:
            return None
        id, member = res
        return to_response_dto(id, member, ClubMembershipResponse)

    async def get_all_member(self, **kargs):
        members = await self.member_repo.get_all(**kargs)
        res = []
        for doc_id, uv in members.items():
            res.append(to_response_dto(doc_id, uv, ClubMembershipResponse))
        return res

    async def create_algo_member(self, member: ClubMembership, actor: str = None):
        if actor:
            await self.verify_club_admin_group(club_id=member.club_id, actor=actor)
        check_member = await self.get_member(
            {"club_id": member.club_id, "user_id": member.user_id}
        )
        if check_member:
            raise CustomHTTPException("member_exist")
        inserted_id = await self.member_repo.insert(member)
        return to_response_dto(inserted_id, member, ClubMembershipResponse)

    async def update_algo_member(self, member_id: str, actor: str, data: Dict):
        member = await self.get_member({"_id": member_id})
        if not member:
            raise CustomHTTPException("member_not_exist")
        await self.verify_club_admin_group(club_id=member.club_id, actor=actor)
        doc_id = await self.member_repo.update_by_id(member_id, data)
        return doc_id

    async def update_algo_member_group(
        self, add: bool, member_id: str, group_id: str, actor: str
    ):
        member = await self.get_member({"_id": member_id})
        if not member:
            raise CustomHTTPException("member_not_exist")
        await self.verify_club_admin_group(club_id=member.club_id, actor=actor)
        member_group = member.group_id
        if add:
            if group_id not in member_group:
                member_group.append(group_id)
        else:
            if group_id in member_group:
                member_group.remove(group_id)
        await self.member_repo.update_by_id(member_id, {"group_id": member_group})
        return member_group

    async def delete_algo_member(self, member_id: str, actor: str):
        member = await self.get_member({"_id": member_id})
        if not member:
            raise CustomHTTPException("member_not_exist")
        await self.verify_club_admin_group(club_id=member.club_id, actor=actor)
        await self.member_repo.delete({"_id": member_id})

    # ========================================================

    async def get_follow(self, query: Dict):
        res = await self.follow_repo.get_one(query)
        if not res:
            return None
        id, follow = res
        return to_response_dto(id, follow, ClubFollowerResponse)

    async def create_algo_follower(self, follower_create: ClubFollower):
        follower = await self.get_follow(
            {"club_id": follower_create.club_id, "user_id": follower_create.user_id}
        )
        if follower:
            raise CustomHTTPException("already_follow")
        doc_id = await self.follow_repo.insert(follower_create)
        return to_response_dto(doc_id, follower_create, ClubFollowerResponse)

    async def delete_algo_follower(self, follower_remove: ClubFollower):
        follower = await self.get_follow(
            {"club_id": follower_remove.club_id, "user_id": follower_remove.user_id}
        )
        if not follower:
            raise CustomHTTPException("not_follow")
        await self.follow_repo.delete(
            {"club_id": follower_remove.club_id, "user_id": follower_remove.user_id}
        )

    async def get_all_follow(self, **kargs):
        follows = await self.follow_repo.get_all(**kargs)
        res = []
        for doc_id, uv in follows.items():
            res.append(to_response_dto(doc_id, uv, ClubFollowerResponse))
        return res
