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


class DateTime:
    DATE_FORMAT: str = "%Y-%m-%d"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    TIME_FORMAT: str = "%H:%M:%S"


class SortOrder(str, Enum):
    ASC = 1
    DESC = -1
