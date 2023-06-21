import asyncio
import threading
import traceback
from collections import deque
from typing import Any, List

from app.core.socket import socket_connection
from app.core.model import SocketPayload


class SocketWorker:
    def __init__(self):
        print("--- socket worker has been created")
        self.__input_data_queue = deque()
        self.__is_locked = False
        self.__flag_event = threading.Event()

        socket_thread = threading.Thread(target=self.__push_wrapper, args=())
        socket_thread.daemon = True
        socket_thread.start()

    def __push_wrapper(self):
        try:
            self.loop = asyncio.get_event_loop()
        except:
            self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(asyncio.wait([self.__push()]))

    def stop_event_loop(self):
        self.loop.stop()

    async def __push(self):
        while True:
            try:
                res = self.__get_latest_data()
                if not res:
                    continue
                await socket_connection.send_data_to_client(res)
            except Exception as e:
                traceback.print_exc()

    def push(self, socket_payload: SocketPayload):
        while not self.__is_locked:
            self.__is_locked = True
            self.__input_data_queue.append(socket_payload)
            self.__is_locked = False
            self.__flag_event.set()
            return None

    def push_many(self, socket_payloads: List[SocketPayload]):
        while not self.__is_locked:
            self.__is_locked = True
            self.__input_data_queue.extend(socket_payloads)
            self.__is_locked = False
            self.__flag_event.set()
            return None

    def __get_latest_data(self):
        if not self.__input_data_queue:
            self.__flag_event.clear()
            self.__flag_event.wait()
        return self.__input_data_queue.popleft()


socket_worker = SocketWorker()
