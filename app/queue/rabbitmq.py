import asyncio
import threading
import traceback
import aio_pika
import pickle
from collections import deque

from app.core.config import project_config
from app.core.constant import Queue
from app.core.log import logger
from app.core.socket import socket_connection
from app.repo.mongo import get_repo


class RabbitMQ:
    def __init__(self):
        self.rabbitmq_url = project_config.RABBITMQ_URL
        self.connection = None
        self.channel = None
        self.queues = {}
        self.__input_data_queue = deque()
        self.__is_locked = False

        mq_thread = threading.Thread(target=self.__work, args=())
        mq_thread.daemon = True
        mq_thread.start()

    def __work(self):
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()

        loop.run_until_complete(asyncio.wait([self.__connect()]))

    async def __create(self):
        while True:
            await asyncio.sleep(0.2)
            try:
                res = self.__get_latest_data()
                if not res:
                    continue
                queue_name, message = res
                await self.__send_message(queue_name, message)
            except Exception as e:
                traceback.print_exc()

    def send(self, queue_name, message):
        while not self.__is_locked:
            self.__is_locked = True
            self.__input_data_queue.append((queue_name, message))
            self.__is_locked = False
            return None

    def __get_latest_data(self):
        if not self.__input_data_queue:
            return None
        return self.__input_data_queue.popleft()

    async def __connect(self):
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        print("Connect to RabbitMQ")

        queue_config = {
            Queue.MAIL: self.__process_mail,
            Queue.SOCKET: self.__process_socket,
            Queue.NOTIFICATION: self.__process_notification,
        }

        tasks = []
        for queue_name, process_func in queue_config.items():
            queue = await self.channel.declare_queue(queue_name)
            self.queues[queue_name] = (queue, process_func)
            task = asyncio.ensure_future(
                self.__consume_and_process(queue, process_func)
            )
            tasks.append(task)
        tasks.append(asyncio.ensure_future(self.__create()))
        await asyncio.gather(*tasks)

    async def __consume_and_process(self, queue, process_func):
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await process_func(message)

    async def __send_message(self, queue_name, message):
        queue, _ = self.queues.get(queue_name, (None, None))
        if queue:
            await self.channel.default_exchange.publish(
                aio_pika.Message(body=pickle.dumps(message)), routing_key=queue.name
            )

    async def __process_notification(self, message):
        message = pickle.loads(message.body)
        document = {"queue": Queue.NOTIFICATION, "message": message}
        logger.log_queue(document)

    async def __process_socket(self, message):
        message = pickle.loads(message.body)
        document = {"queue": Queue.SOCKET, "message": message}
        logger.log_queue(document)
        await socket_connection.send_data(data=message)

    async def __process_mail(self, message):
        message = pickle.loads(message.body)
        document = {"queue": Queue.MAIL, "message": message}
        logger.log_queue(document)


rabbitmq = RabbitMQ()
