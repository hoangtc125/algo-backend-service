from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from app.core.constant import (
    EventType,
    MembershipStatus,
    ClubRole,
    ClubRequestStatus,
    ClubType,
    GroupType,
)
from app.core.model import BaseAuditModel


class Club(BaseAuditModel):
    name: str
    email: str
    nickname: Optional[str] = None
    address: Optional[str] = None
    addressPosition: Optional[Dict] = None
    slogan: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    type: Optional[str] = ClubType.EDU
    rule: Optional[List] = []
    settings: Optional[Dict] = {
        "gen": [],
    }


class ClubResponse(Club):
    id: str
    groups: Optional[List] = []
    followers: Optional[List] = []
    avatar: Optional[Any] = None


class Group(BaseAuditModel):
    club_id: str
    name: str
    description: Optional[str] = None
    type: Optional[str] = GroupType.PERMANANT
    is_remove: bool = True


class GroupResponse(Group):
    id: str
    members: Optional[List] = []


class ClubMembership(BaseAuditModel):
    club_id: str
    role: str = ClubRole.MEMBER
    status: str = MembershipStatus.ACTIVE
    user_id: Optional[str] = None
    group_id: Optional[List] = None
    gen: Optional[str] = None


class ClubMembershipResponse(ClubMembership):
    id: str
    user: Optional[Any] = None


class ClubFollower(BaseAuditModel):
    user_id: str
    club_id: str


class ClubFollowerResponse(ClubFollower):
    id: str
    user: Optional[Any] = None


class ClubRequest(BaseAuditModel):
    user_id: str
    club_id: str
    status: ClubRequestStatus.PROCESSING


class ClubRequestResponse(ClubRequest):
    id: str
    user: Optional[Any] = None


GroupDefault = [
    {
        "custom_id": None,
        "obj": Group(
            club_id=1,
            name="Ban quản lý",
            description="Xây dựng và thực hiện chiến lược phát triển và mục tiêu của CLB.",
            is_remove=False,
        ),
    },
    {
        "custom_id": None,
        "obj": Group(
            club_id=1,
            name="Ban chuyên môn",
            description="Đảm bảo chất lượng và phát triển chuyên môn trong lĩnh vực mà CLB hoạt động.",
        ),
    },
    {
        "custom_id": None,
        "obj": Group(
            club_id=1,
            name="Ban nhân sự",
            description="Tuyển dụng, đào tạo và quản lý thành viên trong CLB.",
        ),
    },
    {
        "custom_id": None,
        "obj": Group(
            club_id=1,
            name="Ban  hậu cần",
            description="Quản lý và duy trì các nguồn tài nguyên vật chất, trang thiết bị và cơ sở vật chất của CLB.",
        ),
    },
    {
        "custom_id": None,
        "obj": Group(
            club_id=1,
            name="Ban truyền thông",
            description="Xây dựng và quản lý chiến lược truyền thông và marketing của CLB.",
        ),
    },
    {
        "custom_id": None,
        "obj": Group(
            club_id=1,
            name="Ban đối ngoại",
            description="Thiết lập và duy trì mối quan hệ với các CLB, tổ chức và cá nhân có liên quan.",
        ),
    },
]


class ClubEvent(BaseAuditModel):
    club_id: str
    group_id: str
    name: str
    description: str
    active_round: str
    start_time: int
    end_time: int
    status: str = None
    type: str = EventType.RECRUIT


class CLubEventResponse(ClubEvent):
    id: str


class Round(BaseAuditModel):
    club_id: str
    event_id: str
    name: str
    description: str
    status: str = None


class FormRound(Round):
    form_question_id: Optional[str] = None


class FormRoundResponse(FormRound):
    id: str


class InterviewRound(Round):
    pass


class InterviewRoundResponse(InterviewRound):
    id: str


class Participant(BaseAuditModel):
    club_id: str
    event_id: str
    email: str
    name: str
    photo_url: Optional[str] = None
    user_id: Optional[str] = None
    status: bool = True


class ParticipantResponse(Participant):
    id: str


class FormQuestion(BaseAuditModel):
    club_id: str
    event_id: str
    sections: List = []


class FormQuestionResponse(FormQuestion):
    id: str


class FormAnswer(FormQuestion):
    form_id: str
    participant_id: str


class FormAnswerResponse(FormAnswer):
    id: str


class Shift(BaseAuditModel):
    club_id: str
    event_id: str
    name: str
    start_time: int
    end_time: int
    place: str
    place_position: Optional[Dict] = None
    capacity: int


class ShiftResponse(Shift):
    id: str


class Appointment(BaseAuditModel):
    club_id: str
    event_id: str
    round_id: str
    shift_ids: List = []
    participant_id: str


class AppointmentResponse(Appointment):
    id: str


if __name__ == "__main__":
    pass
