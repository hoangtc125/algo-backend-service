from typing import Optional

from pydantic import BaseModel

from app.core.model import BaseAuditModel


class Notification(BaseAuditModel):
    content: str
    link: Optional[str] = None
    to: str
    seen: Optional[bool] = False


class NotificationResponse(Notification):
    id: str


class SocketNotification(BaseModel):
    client_id: str = None
    channel: str = "system"
    data: Notification = None
