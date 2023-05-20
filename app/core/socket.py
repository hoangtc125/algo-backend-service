from typing import Any
import socketio

from app.core.model import SocketPayload


class Socket:
    def __init__(self):
        self.__sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self.__asgi = socketio.ASGIApp(self.__sio)
        self.__clients = {}

        @self.__sio.on("connect", namespace="/")
        async def handle_connect(sid, environ):
            client_id = self.get_client_id(environ)
            self.client_connected(sid, client_id)

        @self.__sio.on("disconnect", namespace="/")
        async def handle_disconnect(sid):
            await self.client_disconnected(sid)

        @self.__sio.on("message", namespace="/")
        async def handle_message(sid, data):
            client_id = self.__clients[sid]
            await self.receive_data_from_client(client_id, data)

    async def receive_data_from_client(self, client_id: str, data: Any):
        await self.send_data_to_client(SocketPayload(data=data))

    async def send_data_to_client(self, socket_payload: SocketPayload):
        await self.__sio.emit(
            socket_payload.channel, socket_payload.data, room=socket_payload.client_id
        )

    def client_connected(self, sid, client_id):
        self.__clients[sid] = client_id
        self.__sio.enter_room(sid, client_id)

    async def client_disconnected(self, sid):
        rooms = self.__sio.rooms(sid)
        for room in rooms:
            await self.__sio.close_room(sid, room)

    def get_client_id(self, environ):
        query_params = environ.get("QUERY_STRING", "")
        query_dict = dict(qc.split("=") for qc in query_params.split("&"))
        client_id = query_dict.get("client_id")
        return client_id

    def __call__(self):
        return self.__asgi


socket_connection = Socket()
