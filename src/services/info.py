import json
import os
import platform


from src.config import Config
from src.models import schemas
from src.models.role import UserRole
from src.services.auth.utils import auth
from src.utils import system_info
from src.utils.wsmanager import WSConnectionManager


class InfoApplicationService:

    def __init__(self, config: Config, current_user):
        self._config = config
        self._current_user = current_user

    @auth(is_authenticated=True, roles=[UserRole.ADMIN, UserRole.USER])
    async def get_system_info(self):
        """
        Информация о системе

        """
        return schemas.SystemInfo(
            cpu=system_info.get_cpu_info(),
            ram=system_info.get_ram_info(),
            os=system_info.get_os_info(),
            rom=system_info.get_rom_info(),
            lan=system_info.get_lan_info(),
        )

    async def get_version(self, details: bool = False) -> dict:
        info = {
            "version": self._config.BASE.VERSION,
            "python": platform.python_version()
        }
        if details:
            info.update(
                {
                    "title": os.environ.get("APP_NAME"),
                    "build": os.environ.get("BUILD_NUMBER"),
                    "build_date": os.environ.get("BUILD_DATE"),
                    "branch": os.environ.get("BRANCH_NAME"),
                    "commit_hash": os.environ.get("COMMIT_HASH"),
                }
            )
        return info

    @auth(is_authenticated=True, roles=[UserRole.ADMIN, UserRole.USER])
    async def get_network_info(self):
        return await system_info.get_network_info()


async def stat_worker(app):
    stats_ws: WSConnectionManager = app.state.stats_ws
    if stats_ws.active_connections:
        cpu_stat = schemas.SystemStat(
            cpu=system_info.get_cpu_stat(),
            ram=system_info.get_ram_stat(),
            rom=system_info.get_rom_stat(),
            lan=system_info.get_lan_stat(),
        ).dict()
        await stats_ws.broadcast(json.dumps(cpu_stat))

