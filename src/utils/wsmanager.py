import logging
import time

from fastapi.websockets import WebSocket
from fastapi.websockets import WebSocketState
from fastapi.websockets import WebSocketDisconnect

from src.exceptions import AccessDenied


class WSConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket, code: int = 1000, reason: str = None) -> None:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(code=code, reason=reason)
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, *, message: str | dict | bytes, json_mode: str = "binary"):
        if websocket.client_state == WebSocketState.CONNECTED:
            if isinstance(message, str):
                await websocket.send_text(message)
            elif isinstance(message, dict):
                await websocket.send_json(message, json_mode)
            elif isinstance(message, bytes):
                await websocket.send_bytes(message)
            else:
                raise TypeError("Message type not supported")

    async def receive_text(self, websocket: WebSocket) -> str:
        try:
            return await websocket.receive_text()
        except (WebSocketDisconnect, RuntimeError):
            await self.disconnect(websocket)

    async def broadcast(self, dictionary: dict) -> None:
        for connection in self.active_connections:
            if connection.client_state == WebSocketState.CONNECTED:
                await self.send_message(connection, message=dictionary)
            else:
                await self.disconnect(connection)


def _ws_jwt_auth(func):
    async def wrapper(*args, **kwargs):
        cls_self: WSJWTConnectionManager = args[0]
        websocket: WebSocket = args[1]
        current_user = websocket.scope['user']
        if current_user.access_exp < time.time():
            await cls_self.disconnect(websocket, int(f'{AccessDenied.status_code}0'), AccessDenied.message)
            return
        return await func(*args, **kwargs)

    return wrapper


class WSJWTConnectionManager(WSConnectionManager):
    """
    Менеджер подключений для ws с авторизацией по JWT

    """

    def __init__(self):
        super().__init__()

    @_ws_jwt_auth
    async def send_message(self, websocket: WebSocket, *, message: str | dict | bytes, json_mode: str = "binary"):
        await super().send_message(websocket, message=message, json_mode=json_mode)

    async def receive_text(self, websocket: WebSocket) -> str:
        return await super().receive_text(websocket)
