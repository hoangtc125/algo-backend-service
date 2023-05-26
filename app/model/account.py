from typing import Optional
from pydantic import BaseModel

from app.core.constant import Role, Provider
from app.core.model import BaseAuditModel


class BaseAccount(BaseModel):
    name: Optional[str] = None
    email: str
    photo_url: Optional[str] = None
    verify: Optional[dict] = None
    role: str = Role.USER
    provider: str = Provider.SYSTEM


class Account(BaseAccount, BaseAuditModel):
    hashed_password: Optional[str] = None
    active: Optional[bool] = False


class AccountCreate(BaseAccount, BaseModel):
    password: str


class AccountUpdate(BaseAccount):
    email = None

    @property
    def email(self):
        raise AttributeError("'AccountUpdate' object has no attribute 'email'")


class AccountResponse(Account):
    id: str


class PasswordUpdate(BaseModel):
    id: str
    password: str


if __name__ == "__main__":
    pass
