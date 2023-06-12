from typing import Dict, List, Optional
from pydantic import BaseModel

from app.core.constant import (
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


class Group(BaseAuditModel):
    club_id: str
    name: str
    description: Optional[str] = None
    type: Optional[str] = GroupType.PERMANANT
    is_remove: bool = True


class GroupResponse(Group):
    id: str


class ClubMembership(BaseAuditModel):
    club_id: str
    role: str = ClubRole.MEMBER
    status: str = MembershipStatus.ACTIVE
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    gen: Optional[str] = None


class ClubMembershipResponse(ClubMembership):
    id: str


class ClubFollower(BaseAuditModel):
    user_id: str
    club_id: str


class ClubFollowerResponse(ClubFollower):
    id: str


class ClubRequest(BaseAuditModel):
    user_id: str
    club_id: str
    status: ClubRequestStatus.PROCESSING


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

if __name__ == "__main__":
    pass
