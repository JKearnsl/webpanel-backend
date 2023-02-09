from fastapi.websockets import WebSocket
from fastapi.websockets import WebSocketDisconnect

from src.models.role import UserRole
from src.services.auth.utils import auth
from src.utils.wsmanager import WSConnectionManager


class StatsApplicationService:

    def __init__(self, stats_ws_manager: WSConnectionManager, current_user):
        self._stats_ws_manager = stats_ws_manager
        self._current_user = current_user

    @auth(is_authenticated=True, roles=[UserRole.ADMIN, UserRole.USER])
    async def subscribe_to_stats(self, websocket: WebSocket) -> None:
        await self._stats_ws_manager.connect(websocket)
        while True:
            try:
                command = await websocket.receive_text()
            except (WebSocketDisconnect, RuntimeError):
                break
            if command == "ping":
                await websocket.send_text("pong")
            elif command == "close":
                await self._stats_ws_manager.disconnect(websocket)
            else:
                await websocket.send_text(f"Unknown command: {command}")
