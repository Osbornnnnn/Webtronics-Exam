from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, select
from sqlalchemy import Integer, DateTime, Text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import Base


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)

    user_id = Column(Integer, unique=False, index=True)
    title = Column(Text, unique=True, index=True)
    description = Column(Text, index=True)
    like_count = Column(Integer, index=True, default=0)
    dislike_count = Column(Integer, index=True, default=0)

    created_at = Column(DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    async def create_post(session: AsyncSession, user_id: int, title: str, description: str) -> Posts:
        post = Posts(user_id=user_id, title=title, description=description)
        session.add(post)
        await session.commit()
        return post

    @staticmethod
    async def find_post(session: AsyncSession, post_id: int) -> Posts | None:
        sql = select(Posts).where(Posts.id == post_id)
        res = await session.execute(sql)
        return res.scalars().first()

    @staticmethod
    async def find_posts(session: AsyncSession, user_id: int) -> list[Posts]:
        sql = select(Posts).filter(Posts.user_id == user_id)
        res = await session.execute(sql)
        return res.scalars().all()

    @staticmethod
    async def update_post(session: AsyncSession, post: Posts, title: str = None, description: str = None, like_count: int = None, dislike_count: int = None) -> Posts:
        if title:
            post.title = title
        if description:
            post.description = description
        if like_count:
            post.like_count = like_count
        if dislike_count:
            post.dislike_count = dislike_count
        await session.commit()
        return post

    @staticmethod
    async def delete_post(session: AsyncSession, post: Posts):
        await session.delete(post)
        await session.commit()
