from typing import Optional

from app.core.model import BaseAuditModel


class Notification(BaseAuditModel):
    content: str
    link: Optional[str] = None
    to: str
    seen: Optional[bool] = False


class NotificationResponse(Notification):
    id: str
