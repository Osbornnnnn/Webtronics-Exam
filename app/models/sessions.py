from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, select
from sqlalchemy import Integer, VARCHAR, DateTime
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import Base


class Sessions(Base):
    __tablename__ = "sessions"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)

    user_id = Column(Integer, unique=True, index=True)
    token = Column(VARCHAR(length=512), unique=True, index=True)

    created_at = Column(DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    async def create_session(session: AsyncSession, user_id: int, token: str) -> Sessions:
        sessions = Sessions(user_id=user_id, token=token)
        session.add(sessions)
        await session.commit()
        return sessions

    @staticmethod
    async def find_session_by_user_id(session: AsyncSession, user_id: int) -> Sessions:
        sql = select(Sessions).where(Sessions.user_id == user_id)
        res = await session.execute(sql)
        return res.scalars().first()

    @staticmethod
    async def find_session(session: AsyncSession, token: str) -> Sessions:
        sql = select(Sessions).where(Sessions.token == token)
        res = await session.execute(sql)
        return res.scalars().first()

    @staticmethod
    async def update_session(session: AsyncSession, current_session: Sessions, user_id: int = None, token: str = None) -> Sessions:
        if user_id:
            current_session.user_id = user_id
        if token:
            current_session.token = token
        await session.commit()
        return current_session

    @staticmethod
    async def delete_session(session: AsyncSession, current_session: Sessions):
        await session.delete(current_session)
        await session.commit()
