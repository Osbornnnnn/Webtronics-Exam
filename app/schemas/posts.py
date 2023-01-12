import datetime

from . import Model


class CreatePostSchema(Model):
    title: str
    description: str


class UpdatePostSchema(Model):
    title: str | None
    description: str | None


class PostResponseSchema(Model):
    id: int
    user_id: int
    title: str
    description: str
    like_count: int
    dislike_count: int
    created_at: datetime.datetime
