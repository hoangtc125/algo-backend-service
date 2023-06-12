from typing import Dict, List, Optional
from pydantic import BaseModel

from app.core.constant import MembershipStatus, ClubRole, ClubRequestStatus
from app.core.model import BaseAuditModel


class Club(BaseAuditModel):
    name: str
    email: str
    nickname: Optional[str] = None
    address: Optional[str] = None
    slogan: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
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


class GroupResponse(Club):
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


if __name__ == "__main__":
    pass
