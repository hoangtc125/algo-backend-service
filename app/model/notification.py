from typing import Optional

from pydantic import BaseModel

from app.core.constant import NotiKind
from app.core.model import BaseAuditModel


class Notification(BaseAuditModel):
    content: str
    link: Optional[str] = None
    to: str
    seen: Optional[bool] = False
    kind: Optional[str] = NotiKind.INFO


class NotificationResponse(Notification):
    id: str


class SocketNotification(BaseModel):
    client_id: str = None
    channel: str = "notification"
    data: Notification = None
