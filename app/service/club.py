from typing import Dict

from app.core.exception import CustomHTTPException
from app.core.model import SocketPayload
from app.core.constant import NotiKind, ProcessStatus
from app.core.config import project_config
from app.service.image import ImageService
from app.model.account import Account, AccountResponse
from app.model.notification import Notification, SocketNotification
from app.model.club import *
from app.repo.mongo import get_repo
from app.util.model import get_dict, to_response_dto
from app.util.time import get_current_timestamp, to_datestring
from app.util.mail import make_mail_end_form_round, Email
from app.worker.socket import socket_worker
from app.worker.notification import notification_worker
from app.worker.mail import mail_worker


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
        self.event_repo = get_repo(
            ClubEvent,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
        self.round_repo = get_repo(
            Round,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
        self.participant_repo = get_repo(
            Participant,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
        self.form_question_repo = get_repo(
            FormQuestion,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
        self.form_answer_repo = get_repo(
            FormAnswer,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
        self.shift_repo = get_repo(
            Shift,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
        self.appointment_repo = get_repo(
            Appointment,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )
        self.cluster_repo = get_repo(
            Cluster,
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

    async def verify_event_owner(self, event_id: str, actor: str):
        event = await self.get_event_min({"_id": event_id})
        if not event:
            raise CustomHTTPException("event_not_exist")
        member = await self.get_member(
            {
                "club_id": event.club_id,
                "user_id": actor,
            }
        )
        if not member:
            raise CustomHTTPException("member_not_exist")
        if event.group_id not in member.group_id:
            admin_group = await self.get_group(
                {
                    "club_id": event.club_id,
                    "_id": {"$in": member.group_id},
                    "is_remove": False,
                }
            )
            if not admin_group:
                raise CustomHTTPException("member_invalid_action")
        return (event, member)

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
        res = {}
        if member.user_id:
            try:
                await self.create_algo_follower(
                    ClubFollower(club_id=member.club_id, user_id=member.user_id)
                )
            except:
                pass
            account = await self.get_account({"_id": member.user_id})
            if account:
                res = get_dict(account)
        res["member"] = to_response_dto(inserted_id, member, ClubMembershipResponse)
        return res

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

    # ========================================================

    async def get_event_min(self, query: Dict):
        res = await self.event_repo.get_one(query)
        if not res:
            return None
        id, event = res
        return to_response_dto(id, event, CLubEventResponse)

    async def get_all_event_min(self, **kargs):
        events = await self.event_repo.get_all(**kargs)
        res = []
        for doc_id, uv in events.items():
            res.append(to_response_dto(doc_id, uv, CLubEventResponse))
        return res

    async def get_event(self, query: Dict):
        res = await self.event_repo.get_one(query)
        if not res:
            return None
        id, event = res
        rounds = await self.get_all_round(
            query={"event_id": id, "club_id": event.club_id}
        )
        owners = await self.get_group({"_id": event.group_id})
        club = await self.get_club_min({"_id": event.club_id})
        return CLubEventResponse(
            id=id, rounds=rounds, owners=owners.members, club=club, **get_dict(event)
        )

    async def get_all_event(self, **kargs):
        events = await self.event_repo.get_all(**kargs)
        res = []
        for doc_id, event in events.items():
            rounds = await self.get_all_round(
                query={"event_id": doc_id, "club_id": event.club_id}
            )
            owners = await self.get_group({"_id": event.group_id})
            club = await self.get_club_min({"_id": event.club_id})
            res.append(
                CLubEventResponse(
                    id=doc_id,
                    rounds=rounds,
                    owners=owners.members,
                    club=club,
                    **get_dict(event),
                )
            )
        return res

    async def create_algo_event(self, event: ClubEvent) -> CLubEventResponse:
        check_event = await self.get_event_min(
            {"club_id": event.club_id, "status": ProcessStatus.ON}
        )
        if check_event:
            raise CustomHTTPException("another_recruit_event_on")
        inserted_id = await self.event_repo.insert(event)
        form_round = Round(
            club_id=event.club_id,
            event_id=inserted_id,
            name="Vòng đơn",
            description="Vòng đơn thu thập thông tin tuyển thành viên",
            status=ProcessStatus.NOT_BEGIN,
            kind=RoundType.FORM,
        )
        interview_round = Round(
            club_id=event.club_id,
            event_id=inserted_id,
            name="Vòng phỏng vấn",
            description="Vòng phỏng vấn ứng viên",
            status=ProcessStatus.NOT_BEGIN,
            kind=RoundType.INTERVIEW,
        )
        groups_id = await self.round_repo.insert_many(
            [
                {
                    "custom_id": None,
                    "obj": form_round,
                },
                {
                    "custom_id": None,
                    "obj": interview_round,
                },
            ]
        )
        owners = await self.get_group({"_id": event.group_id})
        return CLubEventResponse(
            id=inserted_id,
            rounds=[
                RoundResponse(id=groups_id[0], **get_dict(form_round)),
                RoundResponse(id=groups_id[1], **get_dict(interview_round)),
            ],
            owners=owners.members,
            **get_dict(event),
        )

    async def update_algo_event(self, event_id: str, actor: str, data: Dict):
        event, _ = await self.verify_event_owner(event_id=event_id, actor=actor)
        doc_id = await self.event_repo.update_by_id(event_id, data)
        notification = Notification(
            content=f"Sự kiện {event.name} đã được cập nhật vào lúc {to_datestring(get_current_timestamp())}",
            to=actor,
            kind=NotiKind.SUCCESS,
        )
        socket_worker.push(
            SocketPayload(
                **get_dict(SocketNotification(client_id=actor, data=notification))
            )
        )
        return doc_id

    # ========================================================

    async def get_round(self, query: Dict):
        res = await self.round_repo.get_one(query)
        if not res:
            return None
        id, round = res
        return to_response_dto(id, round, RoundResponse)

    async def get_all_round(self, **kargs):
        rounds = await self.round_repo.get_all(**kargs)
        res = []
        for doc_id, uv in rounds.items():
            res.append(to_response_dto(doc_id, uv, RoundResponse))
        return res

    async def update_algo_round(
        self, event_id: str, round_id: str, actor: str, data: Dict
    ):
        event, _ = await self.verify_event_owner(event_id=event_id, actor=actor)
        doc_id = await self.round_repo.update_by_id(round_id, data)
        notification = Notification(
            content=f"Sự kiện {event.name} đã được cập nhật vào lúc {to_datestring(get_current_timestamp())}",
            to=actor,
            kind=NotiKind.SUCCESS,
        )
        socket_worker.push(
            SocketPayload(
                **get_dict(SocketNotification(client_id=actor, data=notification))
            )
        )
        return doc_id

    async def end_form_round(self, event_check, participants):
        mails = [
            Email(
                receiver_email=participant.email,
                cc_email=[event_check.club.email],
                subject="Thông báo kết quả vòng đơn ứng tuyển thành viên",
                content=make_mail_end_form_round(
                    event_check.club.name, participant.name, participant.approve[0]
                ),
            )
            for participant in participants
        ]
        mail_worker.push_many(mails)

    # ========================================================

    async def get_participant(self, query: Dict):
        res = await self.participant_repo.get_one(query)
        if not res:
            return None
        id, participant = res
        user = photo = None
        if participant.user_id:
            user = await self.get_account({"_id": participant.user_id})
        if participant.photo_url:
            photo = await ImageService().get_image({"_id": participant.photo_url})
        return ParticipantResponse(
            id=id, user=user, photo=photo, **get_dict(participant)
        )

    async def get_all_participant(self, **kargs):
        participants = await self.participant_repo.get_all(**kargs)
        res = []
        for doc_id, participant in participants.items():
            user = photo = None
            if participant.user_id:
                user = await self.get_account({"_id": participant.user_id})
            if participant.photo_url:
                photo = await ImageService().get_image({"_id": participant.photo_url})
            res.append(
                ParticipantResponse(
                    id=doc_id, user=user, photo=photo, **get_dict(participant)
                )
            )
        return res

    async def create_one_participant(self, participant: Participant):
        doc_id = await self.participant_repo.insert(participant)
        return doc_id

    async def create_many_participant(self, participants: List[Participant]):
        doc_ids = await self.participant_repo.insert_many(
            [{"obj": participant} for participant in participants]
        )
        return doc_ids

    async def update_algo_participant(
        self, event_id: str, participant_id: str, actor: str, data: Dict
    ):
        event, _ = await self.verify_event_owner(event_id=event_id, actor=actor)
        doc_id = await self.participant_repo.update_by_id(participant_id, data)
        return doc_id

    # ========================================================

    async def get_form_question(self, query: Dict):
        res = await self.form_question_repo.get_one(query)
        if not res:
            return None
        id, form_question = res
        answers = await self.get_all_form_answer(
            query={
                "club_id": form_question.club_id,
                "event_id": form_question.event_id,
                "round_id": form_question.round_id,
                "form_id": id,
            }
        )
        return FormQuestionResponse(id=id, answers=answers, **get_dict(form_question))

    async def get_all_form_question(self, **kargs):
        form_questions = await self.form_question_repo.get_all(**kargs)
        res = []
        for doc_id, uv in form_questions.items():
            res.append(to_response_dto(doc_id, uv, FormQuestionResponse))
        return res

    async def create_form_question(
        self, form_question: FormQuestion, custom_id: str = None
    ):
        doc_id = await self.form_question_repo.insert(
            form_question, custom_id=custom_id
        )
        return doc_id

    async def update_algo_form_question(
        self, event_id: str, form_question_id: str, actor: str, data: Dict
    ):
        event, _ = await self.verify_event_owner(event_id=event_id, actor=actor)
        doc_id = await self.form_question_repo.update_by_id(form_question_id, data)
        return doc_id

    # ========================================================

    async def get_form_answer(self, query: Dict):
        res = await self.form_answer_repo.get_one(query)
        if not res:
            return None
        id, form_answer = res
        participant = await self.get_participant({"_id": form_answer.participant_id})
        return FormAnswerResponse(
            id=id, participant=participant, **get_dict(form_answer)
        )

    async def get_all_form_answer(self, **kargs):
        form_answers = await self.form_answer_repo.get_all(**kargs)
        res = []
        for doc_id, form_answer in form_answers.items():
            participant = await self.get_participant(
                {"_id": form_answer.participant_id}
            )
            res.append(
                FormAnswerResponse(
                    id=doc_id, participant=participant, **get_dict(form_answer)
                )
            )
        return res

    async def create_form_answer(self, form_answer: FormAnswer):
        event_check = await self.get_event_min({"_id": form_answer.event_id})
        if event_check.status != ProcessStatus.ON:
            raise CustomHTTPException("form_closed")
        round_check = await self.get_round({"_id": form_answer.round_id})
        if round_check.status != ProcessStatus.ON:
            raise CustomHTTPException("form_closed")
        if not form_answer.participant_id:
            participant_id = await self.create_one_participant(
                Participant(
                    club_id=form_answer.club_id,
                    event_id=form_answer.event_id,
                    email=form_answer.sections[0]["data"][0]["answer"],
                    name=form_answer.sections[0]["data"][1]["answer"],
                    user_id=form_answer.user_id,
                    approve=[False, False],
                )
            )
            form_answer.participant_id = participant_id
        doc_id = await self.form_answer_repo.insert(form_answer)
        return doc_id

    # ========================================================

    async def get_all_shift(self, **kargs):
        shifts = await self.shift_repo.get_all(**kargs)
        res = []
        for doc_id, uv in shifts.items():
            res.append(to_response_dto(doc_id, uv, ShiftResponse))
        return res

    async def create_shift(self, shift: Shift, actor: str):
        event, _ = await self.verify_event_owner(event_id=shift.event_id, actor=actor)
        doc_id = await self.shift_repo.insert(shift)
        return doc_id

    async def udpate_shift(self, event_id: str, shift_id: str, actor: str, data: Dict):
        event, _ = await self.verify_event_owner(event_id=event_id, actor=actor)
        doc_id = await self.shift_repo.update_by_id(shift_id, data)
        return doc_id

    async def delete_shift(self, event_id: str, shift_id: str, actor: str):
        event, _ = await self.verify_event_owner(event_id=event_id, actor=actor)
        await self.shift_repo.delete({"_id": shift_id})
        return None

    # ========================================================

    async def get_all_appointment(self, **kargs):
        appointments = await self.appointment_repo.get_all(**kargs)
        res = []
        for doc_id, uv in appointments.items():
            res.append(to_response_dto(doc_id, uv, AppointmentResponse))
        return res

    async def create_appointment(self, appointment: Appointment):
        doc_id = await self.appointment_repo.insert(appointment)
        return doc_id

    async def udpate_appointment(
        self, event_id: str, appointment_id: str, actor: str, data: Dict
    ):
        event, _ = await self.verify_event_owner(event_id=event_id, actor=actor)
        doc_id = await self.appointment_repo.update_by_id(appointment_id, data)
        return doc_id

    # ========================================================

    async def get_cluster(self, query: Dict):
        res = await self.cluster_repo.get_one(query)
        if not res:
            return None
        id, cluster = res
        return to_response_dto(id, cluster, ClusterResponse)

    async def get_all_cluster(self, **kargs):
        clusters = await self.cluster_repo.get_all(**kargs)
        res = []
        for doc_id, uv in clusters.items():
            res.append(to_response_dto(doc_id, uv, ClusterResponse))
        return res

    async def create_cluster(self, cluster: Cluster, actor: str):
        event, _ = await self.verify_event_owner(event_id=cluster.event_id, actor=actor)
        round_check = await self.get_round({"_id": cluster.round_id})
        if round_check.status != ProcessStatus.PAUSE:
            raise CustomHTTPException("round_not_finished")
        doc_id = await self.cluster_repo.insert(cluster)
        return doc_id
