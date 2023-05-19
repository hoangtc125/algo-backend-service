import threading
import traceback
from collections import deque

from app.util.mail import Email, send_mail


class MailWorker:
    def __init__(self):
        self.__input_data_queue = deque()
        self.__is_locked = False
        self.__flag_event = threading.Event()

        mail_thread = threading.Thread(target=self.__push, args=())
        mail_thread.daemon = True
        mail_thread.start()

    def __push(self):
        while True:
            try:
                res = self.__get_latest_data()
                if not res:
                    continue
                send_mail(res)
            except Exception as e:
                traceback.print_exc()

    def push(self, email: Email):
        while not self.__is_locked:
            self.__is_locked = True
            self.__input_data_queue.append(email)
            self.__is_locked = False
            self.__flag_event.set()
            return None

    def __get_latest_data(self) -> Email:
        if not self.__input_data_queue:
            self.__flag_event.clear()
            self.__flag_event.wait()
        return self.__input_data_queue.popleft()


mail_worker = MailWorker()
