
from fastapi.websockets import WebSocket
from starlette.websockets import WebSocketState

from src.models import schemas
from src.models.role import UserRole
from src.services.auth.utils import filters
from src.utils import system_info
from src.utils.wsmanager import WSJWTConnectionManager


class StatsApplicationService:

    def __init__(self, stats_ws_manager: WSJWTConnectionManager, current_user):
        self._stats_ws_manager = stats_ws_manager
        self._current_user = current_user

    @filters(roles=[UserRole.ADMIN, UserRole.USER])
    async def subscribe_to_stats(self, websocket: WebSocket) -> None:
        await self._stats_ws_manager.connect(websocket)
        while websocket.client_state == WebSocketState.CONNECTED:
            command = await self._stats_ws_manager.receive_text(websocket)
            if command == "ping":
                await self._stats_ws_manager.send_message(websocket, message="pong")
            elif command == "close":
                await self._stats_ws_manager.disconnect(websocket)
            else:
                await self._stats_ws_manager.send_message(websocket, message=f"Unknown command: {command}")


async def stat_worker(app):
    stats_ws: WSJWTConnectionManager = app.state.stats_ws
    if stats_ws.active_connections:
        cpu_stat = schemas.SystemStat(
            cpu=system_info.get_cpu_stat(),
            ram=system_info.get_ram_stat(),
            rom=system_info.get_rom_stat(),
            lan=system_info.get_lan_stat(),
        ).dict()
        await stats_ws.broadcast(cpu_stat)
