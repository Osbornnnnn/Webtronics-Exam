from fastapi import APIRouter, status, Security, Depends, Query
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_session
from ..dependencies import HTTPBearerScheme
from ..models.posts import Posts
from ..pkg.cryptography import PayloadSchema
from ..responses import HTTPError
from ..schemas.posts import PostResponseSchema, CreatePostSchema, UpdatePostSchema

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    body: CreatePostSchema, payload: PayloadSchema = Security(HTTPBearerScheme), session: AsyncSession = Depends(get_session)
) -> PostResponseSchema:
    try:
        post = await Posts.create_post(session, user_id=payload.user_id, **body.dict())
    except IntegrityError as e:
        raise HTTPError(status=status.HTTP_409_CONFLICT, message="post is exist", error=str(e.orig).split("DETAIL:  ")[1])

    return PostResponseSchema(**post.__dict__)


@router.get("/", status_code=status.HTTP_200_OK, dependencies=[Security(HTTPBearerScheme)])
async def get_posts(payload: PayloadSchema = Security(HTTPBearerScheme), user_id: int | None = Query(default=None), session: AsyncSession = Depends(get_session)) -> list[PostResponseSchema]:
    if not user_id:
        user_id = payload.user_id

    posts = await Posts.find_posts(session, user_id=user_id)

    if not posts:
        raise HTTPError(status=status.HTTP_404_NOT_FOUND, message="user not have posts")

    return [PostResponseSchema(**post.__dict__) for post in posts]


@router.get("/{post_id}", status_code=status.HTTP_200_OK, dependencies=[Security(HTTPBearerScheme)])
async def get_post(post_id: int, session: AsyncSession = Depends(get_session)) -> PostResponseSchema:
    post = await Posts.find_post(session, post_id=post_id)
    if not post:
        raise HTTPError(status=status.HTTP_404_NOT_FOUND, message="post is not exist")

    return PostResponseSchema(**post.__dict__)


@router.put("/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(post_id: int, body: UpdatePostSchema, payload: PayloadSchema = Security(HTTPBearerScheme), session: AsyncSession = Depends(get_session)) -> PostResponseSchema:
    post = await Posts.find_post(session, post_id=post_id)

    if not post:
        raise HTTPError(status=status.HTTP_404_NOT_FOUND, message="post is not exist")

    if post.user_id != payload.user_id:
        raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="not enough permission")

    post = await Posts.update_post(session, post, **body.dict())

    return PostResponseSchema(**post.__dict__)


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, payload: PayloadSchema = Security(HTTPBearerScheme), session: AsyncSession = Depends(get_session)) -> PostResponseSchema:
    post = await Posts.find_post(session, post_id=post_id)

    if post.user_id != payload.user_id:
        raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="not enough permission")

    try:
        await Posts.delete_post(session, post)
    except NoResultFound as e:
        raise HTTPError(status=status.HTTP_404_NOT_FOUND, message="post is not exist", error=e.__str__())

    return PostResponseSchema(**post.__dict__)


@router.post("/{post_id}/like", status_code=status.HTTP_200_OK)
async def like_post(post_id: int, payload: PayloadSchema = Security(HTTPBearerScheme), session: AsyncSession = Depends(get_session)) -> PostResponseSchema:
    post = await Posts.find_post(session, post_id=post_id)

    if post.user_id == payload.user_id:
        raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="cant like yourself post")

    post = await Posts.update_post(session, post, like_count=post.like_count+1)

    return PostResponseSchema(**post.__dict__)


@router.post("/{post_id}/dislike", status_code=status.HTTP_200_OK)
async def dislike_post(post_id: int, payload: PayloadSchema = Security(HTTPBearerScheme), session: AsyncSession = Depends(get_session)) -> PostResponseSchema:
    post = await Posts.find_post(session, post_id=post_id)

    if post.user_id == payload.user_id:
        raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="cant dislike yourself post")

    post = await Posts.update_post(session, post, dislike_count=post.dislike_count+1)

    return PostResponseSchema(**post.__dict__)
