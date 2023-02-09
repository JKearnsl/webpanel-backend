from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, ValidationError

from src.models.notify_level import NotifyLevel


class Notification(BaseModel):
    """
    Модель уведомления

    """
    id: str
    title: str
    description: str
    created_at: datetime
    level: NotifyLevel

