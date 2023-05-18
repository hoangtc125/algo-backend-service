from typing import Dict

from app.core.exception import CustomHTTPException
from app.core.config import project_config
from app.core.socket import socket_connection
from app.model.notification import Notification, NotificationResponse
from app.repo.mongo import get_repo
from app.util.model import get_dict, to_response_dto


class NotificationService:
    def __init__(self):
        self.notification_repo = get_repo(
            Notification,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )

    async def get_all(self, page_size: int = 20, page_number: int = None):
        accounts = await self.notification_repo.get_all(
            page_size=page_size, page_number=page_number
        )
        res = []
        for doc_id, uv in accounts.items():
            res.append(to_response_dto(doc_id, uv, NotificationResponse))
        return res
