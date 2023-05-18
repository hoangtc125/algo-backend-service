import asyncio
import threading
import traceback
from collections import deque

from app.core.socket import socket_connection


class SocketWorker:
    def __init__(self):
        self.__input_data_queue = deque()
        self.__is_locked = False
        self.__flag_event = threading.Event()

        logger_thread = threading.Thread(target=self.__push_wrapper, args=())
        logger_thread.daemon = True
        logger_thread.start()

    def __push_wrapper(self):
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
        loop.run_until_complete(asyncio.wait([self.__push()]))

    async def __push(self):
        while True:
            try:
                res = self.__get_latest_data()
                if not res:
                    continue
                event, data = res
                await socket_connection.send_data(channel=event, data=data)
            except Exception as e:
                traceback.print_exc()

    def push(self, data, event: str = "system"):
        while not self.__is_locked:
            self.__is_locked = True
            self.__input_data_queue.append((event, data))
            self.__is_locked = False
            self.__flag_event.set()
            return None

    def __get_latest_data(self):
        if not self.__input_data_queue:
            self.__flag_event.clear()
            self.__flag_event.wait()
        return self.__input_data_queue.popleft()


socket_worker = SocketWorker()
