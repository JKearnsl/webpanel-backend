import json
import secrets
import string
from datetime import datetime
from typing import Optional

from src.models import schemas
from src.models.notify_level import NotifyLevel
from src.utils import RedisClient


class NotificationApplicationService:

    def __init__(self, current_user, redis_client):
        self._current_user = current_user
        self._redis_client: RedisClient = redis_client

    async def get_push_notification(self) -> Optional[schemas.Notification]:
        """
        Получить одно пуш-уведомление из очереди

        """
        notifications = await self._redis_client.find_keys("notify*")
        await self._redis_client.delete() # todo


async def create_push_notification(
        title: str,
        description: str,
        level: NotifyLevel,
        redis_client: RedisClient
) -> None:
    """
    Создать уведомление

    """
    key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4, 30))
    value = json.dumps({
        "title": title,
        "description": description,
        "level": level.value,
        "created_at": datetime.now().isoformat()
    })
    await redis_client.set(key, value, expire=60 * 60 * 24)

