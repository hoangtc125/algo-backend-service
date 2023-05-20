import logging
import os, sys
import threading
import traceback
from collections import deque
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from logging.handlers import TimedRotatingFileHandler

from app.core.config import project_config
from app.core.api import API_PERMISSION
from app.util.time import get_current_timestamp


class MyTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename: str):
        self.__file_name = filename
        self.__base_dir = self.create_dir()
        TimedRotatingFileHandler.__init__(
            self,
            self.__base_dir + "/" + self.__file_name + ".ini",
            when="midnight",
            interval=1,
        )

    def doRollover(self):
        self.__base_dir = self.create_dir()
        self.stream.close()
        self.stream = open(
            self.__base_dir + "/" + self.__file_name + ".ini", "+a", encoding="utf-8"
        )
        self.rolloverAt = self.rolloverAt + self.interval

    @staticmethod
    def create_dir(f_date_fmt="YYYY/mm/dd"):
        base_dir = (
            project_config.LOG_DIR + "/" + str(datetime.now().date()).replace("-", "/")
        )
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        return base_dir


class Logger:
    def __init__(self):
        self.__pool = {}
        self.__input_data_queue = deque()
        self.__is_locked = False
        self.__flag_event = threading.Event()
        self.__routers = Logger.get_dir_mapping()

        loggers = {}
        for router in self.__routers:
            _logger = Logger.create_file_handler(src=router, dst=router)
            loggers[router] = {
                "critical": _logger.critical,
                "warning": _logger.warning,
                "debug": _logger.debug,
                "error": _logger.error,
                "info": _logger.info,
            }
        self.__loggers = loggers

        logger_thread = threading.Thread(target=self.__log, args=())
        logger_thread.daemon = True
        logger_thread.start()

    @property
    def level(self):
        class Level:
            CRITICAL: str = "critical"
            WARNING: str = "warning"
            DEBUG: str = "debug"
            ERROR: str = "error"
            INFO: str = "info"

        return Level

    @property
    def tag(self):
        class Tag:
            START: str = "start"
            ADD: str = "add"
            END: str = "end"
            QUEUE: str = "queue"

        return Tag

    def __log(self):
        while True:
            try:
                # if self.__pool:
                #     newest_id, newest_msg = list(self.__pool.items())[0]
                #     if newest_msg["expired_at"] <= get_current_timestamp():
                #         newest_msg["data"].append(
                #             (
                #                 "\n=================================================\n",
                #                 logger.level.DEBUG,
                #             )
                #         )
                #         for data in newest_msg["data"]:
                #             _message, _level = data
                #             self.__loggers["timeout"][_level](_message)
                #         self.__pool.pop(newest_id)

                res = self.__get_latest_data()
                if not res:
                    continue

                request_id, latest_data, tag, level = res

                if tag == self.tag.QUEUE:
                    self.__loggers["queue"][level](str(latest_data))
                    continue

                if tag == self.tag.START:
                    self.__pool[request_id] = {}
                    self.__pool[request_id]["data"] = []
                    # self.__pool[request_id]["expired_at"] = (
                    #     get_current_timestamp() + project_config.LOG_TIME_OUT
                    # )

                    request, request_user = latest_data
                    if request_user:
                        self.__pool[request_id]["data"].append(
                            (
                                f"USER: {request_user.username}, ROLE: {request_user.role}",
                                level,
                            )
                        )
                    if request:
                        self.__pool[request_id]["data"].append(
                            (f"CLIENT: client={request.client}", level)
                        )
                        self.__pool[request_id]["data"].append(
                            (
                                f"REQUEST: method={request.method}, url={request.url}",
                                level,
                            )
                        )
                    continue

                if request_id not in self.__pool.keys():
                    self.__pool[request_id] = {}
                    self.__pool[request_id]["data"] = []
                    # self.__pool[request_id]["expired_at"] = (
                    #     get_current_timestamp() + project_config.LOG_TIME_OUT
                    # )

                if tag == self.tag.ADD:
                    self.__pool[request_id]["data"].extend(
                        [(str(msg), level) for msg in latest_data]
                    )
                    continue

                path, response = latest_data
                if response:
                    self.__pool[request_id]["data"].append(
                        (
                            f"RESPONSE: status={response.status_code}, process_time={response.headers['X-Process-Time']}",
                            level,
                        )
                    )
                else:
                    self.__pool[request_id]["data"].append(("RESPONSE: None", level))
                self.__pool[request_id]["data"].append(
                    ("\n=================================================\n", level)
                )

                router = path.split("/")[1]
                if router not in self.__routers:
                    router = "stranger"

                for data in self.__pool[request_id]["data"]:
                    _message, _level = data
                    self.__loggers[router][_level](f"{request_id} - {_message}")
                self.__pool.pop(request_id)
            except Exception as e:
                traceback.print_exc()

    def log(self, *args, tag="add", level="info"):
        request_id = Logger.get_http_request_id(sys._getframe(0))
        while not self.__is_locked:
            self.__is_locked = True
            self.__input_data_queue.append((request_id, args, tag, level))
            self.__is_locked = False
            self.__flag_event.set()
            return None

    def log_queue(self, *args, tag="queue", level="info"):
        while not self.__is_locked:
            self.__is_locked = True
            self.__input_data_queue.append((None, args, tag, level))
            self.__is_locked = False
            self.__flag_event.set()
            return None

    def __get_latest_data(self):
        if not self.__input_data_queue:
            self.__flag_event.clear()
            self.__flag_event.wait()
        return self.__input_data_queue.popleft()

    @staticmethod
    def get_http_request_id(frame=sys._getframe(0), context=1):
        while frame:
            if "self" in frame.f_locals.keys() and isinstance(
                frame.f_locals["self"], BaseHTTPMiddleware
            ):
                return id(frame.f_locals["scope"])
            frame = frame.f_back
        return 1

    @staticmethod
    def get_dir_mapping():
        first_elements = set()  # Tạo một set để lưu trữ các phần tử duy nhất
        first_elements.add("stranger")
        first_elements.add("queue")
        first_elements.add("timeout")
        for path in API_PERMISSION:
            elements = path.split("/")  # Tách chuỗi theo dấu "/"
            first_element = elements[1]  # Lấy phần tử đầu tiên sau dấu "/"
            first_elements.add(first_element)  # Thêm phần tử vào set
        return list(first_elements)

    @staticmethod
    def create_file_handler(src, dst):
        logger = logging.getLogger(src)
        logger.setLevel(logging.DEBUG)
        f_format = logging.Formatter(
            "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
        )
        f_handler = MyTimedRotatingFileHandler(filename=dst)
        f_handler.setFormatter(f_format)
        f_handler.suffix = "%Y-%m-%d"
        logger.addHandler(f_handler)
        return logger


logger = Logger()
