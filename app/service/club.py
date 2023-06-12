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

    async def get_club(self, query: Dict):
        res = await self.club_repo.get_one(query)
        if not res:
            return None
        id, club = res
        return to_response_dto(id, club, ClubResponse)

    async def get_all(self, **kargs):
        clubs = await self.club_repo.get_all(**kargs)
        res = []
        for doc_id, uv in clubs.items():
            res.append(to_response_dto(doc_id, uv, ClubResponse))
        return res

    async def create_algo_club(self, club: Club) -> ClubResponse:
        inserted_id = await self.club_repo.insert(club)
        return to_response_dto(inserted_id, club, ClubResponse)

    async def delete_algo_club(self, club_id: str, actor: str):
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
        try:
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
        except:
            traceback.print_exc()

    # ========================================================

    async def get_member(self, query: Dict):
        res = await self.member_repo.get_one(query)
        if not res:
            return None
        id, member = res
        return to_response_dto(id, member, ClubMembershipResponse)

    async def create_algo_member(self, member: ClubMembership):
        inserted_id = await self.member_repo.insert(member)
        return to_response_dto(inserted_id, member, ClubMembershipResponse)

    # ========================================================

    async def create_algo_follower(self, follower: ClubFollower):
        inserted_id = await self.follow_repo.insert(follower)
        return to_response_dto(inserted_id, follower, ClubFollowerResponse)
