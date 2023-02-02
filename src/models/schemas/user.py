from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, ValidationError

from src.models.role import UserRole
from src.utils import validators


class User(BaseModel):
    """
    Базовая схема пользователя
    """
    id: int
    username: str
    email: str
    role: UserRole
    create_at: datetime
    update_at: Optional[datetime]

    class Config:
        orm_mode = True


class UserSignUp(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole

    @validator('username')
    def username_len(cls, value):
        if not validators.is_valid_username(value):
            raise ValidationError
        return value

    @validator('email')
    def email_must_be_valid(cls, value):
        if not validators.is_valid_email(value):
            raise ValidationError
        return value

    @validator('password')
    def password_must_be_valid(cls, value):
        if not validators.is_valid_password(value):
            raise ValidationError
        return value


class UserSignIn(BaseModel):
    username: str
    password: str

    @validator('username')
    def username_len(cls, value):
        if not validators.is_valid_username(value):
            raise ValidationError
        return value

    @validator('password')
    def password_must_be_valid(cls, value):
        if not validators.is_valid_password(value):
            raise ValidationError
        return value


class UserUpdate(BaseModel):
    username: Optional[str]
