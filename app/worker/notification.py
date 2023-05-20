import asyncio
import threading
import traceback
from collections import deque

from app.core.config import project_config
from app.repo.mongo import get_repo
from app.model.notification import Notification


class NotificationWorker:
    def __init__(self):
        print("--- notification worker has been created")
        self.__input_data_queue = deque()
        self.__is_locked = False
        self.__flag_event = threading.Event()

        notification_thread = threading.Thread(target=self.__create_wrapper, args=())
        notification_thread.daemon = True
        notification_thread.start()

    def __create_wrapper(self):
        try:
            self.loop = asyncio.get_event_loop()
        except:
            self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(asyncio.wait([self.__create()]))

    def stop_event_loop(self):
        self.loop.stop()

    async def __create(self):
        notification_repo = get_repo(
            Notification,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=True,
        )
        while True:
            try:
                res = self.__get_latest_data()
                if not res:
                    continue
                await notification_repo.insert(res)
            except Exception as e:
                traceback.print_exc()

    def create(self, notification_create: Notification):
        while not self.__is_locked:
            self.__is_locked = True
            self.__input_data_queue.append(notification_create)
            self.__is_locked = False
            self.__flag_event.set()
            return None

    def __get_latest_data(self):
        if not self.__input_data_queue:
            self.__flag_event.clear()
            self.__flag_event.wait()
        return self.__input_data_queue.popleft()


notification_worker = NotificationWorker()
