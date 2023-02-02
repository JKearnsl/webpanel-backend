from pydantic import BaseModel, validator

from src.models.role import UserRole
from src.models.schemas import User


class UserBigResponse(User):
    pass


class UserSmallResponse(BaseModel):

    id: int
    role: UserRole
    username: str

    class Config:
        orm_mode = True
