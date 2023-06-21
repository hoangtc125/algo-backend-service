from enum import Enum


class Role:
    ADMIN = "ADMIN"
    USER = "USER"

    @staticmethod
    def get_all():
        return [Role.ADMIN, Role.USER]


class Provider:
    SYSTEM = "SYSTEM"
    FIREBASE = "FIREBASE"


class NotiKind:
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"


class DateTime:
    DATE_FORMAT: str = "%Y-%m-%d"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    TIME_FORMAT: str = "%H:%M:%S"


class SortOrder(str, Enum):
    ASC = 1
    DESC = -1


class Queue:
    NOTIFICATION = "notification"
    SOCKET = "socket"


class School(str, Enum):
    HUST = "HUST"
    HUST2 = "HUST2"
    HUCE = "HUCE"
    NEU = "NEU"
    NEU2 = "NEU2"


class ClubRole:
    PRESIDENT: str = "PRESIDENT"
    SUB_PRESIDENT: str = "SUB_PRESIDENT"
    LEADER: str = "LEADER"
    SUB_LEADER: str = "SUB_LEADER"
    MEMBER: str = "MEMBER"


class MembershipStatus:
    ACTIVE: str = "ACTIVE"
    PAUSE: str = "PAUSE"
    INACTIVE: str = "INACTIVE"


class ClubRequestStatus:
    PROCESSING: str = "PROCESSING"
    PASS: str = "PASS"
    REJECT: str = "REJECT"


class ClubGroup:
    ADMIN: str = "ADMIN"
    CHUYEN_MON: str = "CHUYEN_MON"
    NHAN_SU: str = "NHAN_SU"
    HAU_CAN: str = "HAU_CAN"
    DOI_NGOAI: str = "DOI_NGOAI"
    TRUYEN_THONG: str = "TRUYEN_THONG"


class ClubType:
    EDU: str = "EDU"


class GroupType:
    TEMP: str = "TEMP"
    PERMANANT: str = "PERMANANT"


class EventType:
    RECRUIT: str = "RECRUIT"


class RoundType:
    FORM: str = "FORM"
    INTERVIEW: str = "INTERVIEW"
