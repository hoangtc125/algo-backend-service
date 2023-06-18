from typing import Dict

from app.core.exception import CustomHTTPException
from app.core.model import SocketPayload
from app.core.constant import NotiKind
from app.core.config import project_config
from app.service.image import ImageService
from app.model.account import Account, AccountResponse
from app.model.notification import Notification, SocketNotification
from app.model.club import *
from app.repo.mongo import get_repo
from app.util.model import get_dict, to_response_dto
from app.util.time import get_current_timestamp, to_datestring
from app.worker.socket import socket_worker
from app.worker.notification import notification_worker


class ClubService:
    def __init__(self):
        self.account_repo = get_repo(
            Account,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
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

    async def get_account(self, query: Dict):
        res = await self.account_repo.get_one(query)
        if not res:
            return None
        id, account = res
        return to_response_dto(id, account, AccountResponse)

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

    async def get_club_min(self, query: Dict):
        res = await self.club_repo.get_one(query)
        if not res:
            return None
        id, club = res
        return to_response_dto(id, club, ClubResponse)

    async def get_all_club_min(self, **kargs):
        clubs = await self.club_repo.get_all(**kargs)
        res = []
        for doc_id, uv in clubs.items():
            res.append(to_response_dto(doc_id, uv, ClubResponse))
        return res

    async def get_club(self, query: Dict):
        res = await self.club_repo.get_one(query)
        if not res:
            return None
        id, club = res
        avatar = None
        if club.image:
            avatar = await ImageService().get_image(query={"_id": club.image})
        groups = await self.get_all_group(
            query={"club_id": id, "type": GroupType.PERMANANT}
        )
        followers = await self.get_all_follow(query={"club_id": id})
        return ClubResponse(
            id=id, groups=groups, followers=followers, avatar=avatar, **get_dict(club)
        )

    async def get_all_club(self, **kargs):
        clubs = await self.club_repo.get_all(**kargs)
        res = []
        for doc_id, club in clubs.items():
            avatar = None
            if club.image:
                avatar = await ImageService().get_image(query={"_id": club.image})
            groups = await self.get_all_group(
                query={"club_id": doc_id, "type": GroupType.PERMANANT}
            )
            followers = await self.get_all_follow(query={"club_id": doc_id})
            res.append(
                ClubResponse(
                    id=doc_id,
                    groups=groups,
                    followers=followers,
                    avatar=avatar,
                    **get_dict(club),
                )
            )
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

    async def get_group_min(self, query: Dict):
        res = await self.group_repo.get_one(query)
        if not res:
            return None
        id, group = res
        return to_response_dto(id, group, GroupResponse)

    async def get_all_group_min(self, **kargs):
        groups = await self.group_repo.get_all(**kargs)
        res = []
        for doc_id, uv in groups.items():
            res.append(to_response_dto(doc_id, uv, GroupResponse))
        return res

    async def get_group(self, query: Dict):
        res = await self.group_repo.get_one(query)
        if not res:
            return None
        id, group = res
        members = await self.get_all_member(
            query={"club_id": group.club_id, "group_id": {"$in": [id]}}
        )
        return GroupResponse(id=id, members=members, **get_dict(group))

    async def get_all_group(self, **kargs):
        groups = await self.group_repo.get_all(**kargs)
        res = []
        for doc_id, group in groups.items():
            members = await self.get_all_member(
                query={"club_id": group.club_id, "group_id": {"$in": [doc_id]}}
            )
            res.append(GroupResponse(id=doc_id, members=members, **get_dict(group)))
        return res

    async def create_algo_group(self, group: Group) -> GroupResponse:
        club = await self.get_club_min(query={"_id": group.club_id})
        if not club:
            raise CustomHTTPException("club_not_exist")
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

    async def get_member_min(self, query: Dict):
        res = await self.member_repo.get_one(query)
        if not res:
            return None
        id, member = res
        return to_response_dto(id, member, ClubMembershipResponse)

    async def get_all_member_min(self, **kargs):
        members = await self.member_repo.get_all(**kargs)
        res = []
        for doc_id, uv in members.items():
            res.append(to_response_dto(doc_id, uv, ClubMembershipResponse))
        return res

    async def get_member(self, query: Dict):
        res = await self.member_repo.get_one(query)
        if not res:
            return None
        id, member = res
        user = await self.get_account({"_id": member.user_id})
        return ClubMembershipResponse(id=id, user=user, **get_dict(member))

    async def get_all_member(self, **kargs):
        members = await self.member_repo.get_all(**kargs)
        res = []
        for doc_id, member in members.items():
            user = await self.get_account({"_id": member.user_id})
            res.append(ClubMembershipResponse(id=doc_id, user=user, **get_dict(member)))
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

    async def get_follow_min(self, query: Dict):
        res = await self.follow_repo.get_one(query)
        if not res:
            return None
        id, follow = res
        return to_response_dto(id, follow, ClubFollowerResponse)

    async def get_all_follow_min(self, **kargs):
        follows = await self.follow_repo.get_all(**kargs)
        res = []
        for doc_id, uv in follows.items():
            res.append(to_response_dto(doc_id, uv, ClubFollowerResponse))
        return res

    async def get_follow(self, query: Dict):
        res = await self.follow_repo.get_one(query)
        if not res:
            return None
        id, follow = res
        user = await self.get_account({"_id": follow.user_id})
        return ClubFollowerResponse(id=id, user=user, **get_dict(follow))

    async def get_all_follow(self, **kargs):
        follows = await self.follow_repo.get_all(**kargs)
        res = []
        for doc_id, follow in follows.items():
            user = await self.get_account({"_id": follow.user_id})
            res.append(ClubFollowerResponse(id=doc_id, user=user, **get_dict(follow)))
        return res

    async def create_algo_follower(self, follower_create: ClubFollower):
        club = await self.get_club_min(query={"_id": follower_create.club_id})
        if not club:
            raise CustomHTTPException("club_not_exist")
        follower = await self.get_follow(
            {"club_id": follower_create.club_id, "user_id": follower_create.user_id}
        )
        if follower:
            raise CustomHTTPException("already_follow")
        doc_id = await self.follow_repo.insert(follower_create)
        return to_response_dto(doc_id, follower_create, ClubFollowerResponse)

    async def delete_algo_follower(self, follower_remove: ClubFollower):
        club = await self.get_club_min(query={"_id": follower_remove.club_id})
        if not club:
            raise CustomHTTPException("club_not_exist")
        follower = await self.get_follow(
            {"club_id": follower_remove.club_id, "user_id": follower_remove.user_id}
        )
        if not follower:
            raise CustomHTTPException("not_follow")
        await self.follow_repo.delete(
            {"club_id": follower_remove.club_id, "user_id": follower_remove.user_id}
        )

    async def get_user_info(self, user_id: str):
        members = await self.get_all_member_min(query={"user_id": user_id})
        member_club_mapping = {member.club_id: {"member": member} for member in members}
        member_clubs = await self.get_all_club_min(
            query={"_id": {"$in": list(member_club_mapping.keys())}}
        )
        for club in member_clubs:
            mapping = member_club_mapping.get(club.id)
            if mapping:
                if club.image:
                    club.avatar = await ImageService().get_image({"_id": club.image})
                mapping["club"] = club

        follows = await self.get_all_follow_min(query={"user_id": user_id})
        follow_club_mapping = {follow.club_id: {"follow": follow} for follow in follows}
        follow_clubs = await self.get_all_club_min(
            query={"_id": {"$in": list(follow_club_mapping.keys())}}
        )
        for club in follow_clubs:
            mapping = follow_club_mapping.get(club.id)
            if mapping:
                if club.image:
                    club.avatar = await ImageService().get_image({"_id": club.image})
                mapping["club"] = club

        return (list(member_club_mapping.values()), list(follow_club_mapping.values()))
