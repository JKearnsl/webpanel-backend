from sqlalchemy import Column, String, Integer, Enum, DateTime, func, Boolean, BigInteger
from sqlalchemy.orm import relationship

from src.db import Base, IntEnum

from src.models.role import UserRole
from src.models.state import UserStates


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), default=UserRole.USER)
    state = Column(IntEnum(UserStates), default=UserStates.ACTIVE)

    create_at = Column(DateTime(timezone=True), server_default=func.now())
    update_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
