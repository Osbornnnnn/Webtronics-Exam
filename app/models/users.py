from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, select, or_
from sqlalchemy import Integer, VARCHAR, DateTime
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)

    username = Column(VARCHAR(length=64), unique=True, nullable=False, index=True)
    full_name = Column(VARCHAR(length=64), nullable=False, index=True)

    email = Column(VARCHAR(length=64), nullable=False, unique=True, index=True)
    password = Column(VARCHAR(length=128), nullable=False, index=True)

    created_at = Column(DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    async def create_user(session: AsyncSession, full_name: str, username: str, email: str, password: str) -> Users:
        user = Users(full_name=full_name, username=username, email=email, password=password)
        session.add(user)
        await session.commit()
        return user

    @staticmethod
    async def find_user(session: AsyncSession, id: int = None, username: str = None, email: str = None) -> Users:
        sql = select(Users).filter(or_(Users.id == id, Users.username == username, Users.email == email))
        res = await session.execute(sql)
        return res.scalars().first()
