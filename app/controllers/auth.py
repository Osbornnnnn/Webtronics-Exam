from __future__ import annotations

import datetime

import jwt
from fastapi import APIRouter, status, Depends, Response, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config
from ..database.connection import get_session
from ..models.sessions import Sessions
from ..models.users import Users
from ..pkg import JWT, Hashlibrary
from ..responses import HTTPError, HTTPSuccess
from ..schemas.auth import SigninSchema, SignupSchema, AccessTokenSchema

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    dependencies=[],
)

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_tokens(request: Request, response: Response, session: AsyncSession = Depends(get_session)) -> AccessTokenSchema:
    refresh_token = request.cookies.get(config.REFRESH_TOKEN_KEY)

    current_session = await Sessions.find_session(session, token=refresh_token)
    if not current_session:
        response.delete_cookie(key=config.REFRESH_TOKEN_KEY)
        raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="invalid session")

    try:
        payload = await JWT.verify_token(refresh_token)
    except jwt.exceptions.ExpiredSignatureError as e:
        response.delete_cookie(key=config.REFRESH_TOKEN_KEY)
        raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="refresh token expired", error=e.__str__(), headers={"WWW-Authenticate": "Bearer"})
    except jwt.exceptions.InvalidSignatureError as e:
        response.delete_cookie(key=config.REFRESH_TOKEN_KEY)
        raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="invalid refresh token", error=e.__str__(), headers={"WWW-Authenticate": "Bearer"})
    except jwt.exceptions.DecodeError as e:
        response.delete_cookie(key=config.REFRESH_TOKEN_KEY)
        raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="invalid refresh token", error=e.__str__(), headers={"WWW-Authenticate": "Bearer"})

    access_token = await JWT.create_token(user_id=payload.user_id, timedelta=datetime.timedelta(seconds=config.ACCESS_TOKEN_EXPIRE))
    refresh_token = await JWT.create_token(user_id=payload.user_id, timedelta=datetime.timedelta(seconds=config.REFRESH_TOKEN_EXPIRE))

    response.set_cookie(
        key=config.REFRESH_TOKEN_KEY,
        value=refresh_token,
        max_age=config.REFRESH_TOKEN_EXPIRE,
        expires=config.REFRESH_TOKEN_EXPIRE,
        path="/",
        domain="",
        httponly=True,
        secure=False
    )

    return AccessTokenSchema(access_token=access_token)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_an_account(body: SignupSchema, response: Response, session: AsyncSession = Depends(get_session)) -> AccessTokenSchema:
    body.password = Hashlibrary.SHA256(body.password)

    try:
        user = await Users.create_user(session, **body.dict())
    except IntegrityError as e:
        raise HTTPError(status=status.HTTP_409_CONFLICT, message="username or email is exist", error=str(e.orig).split("DETAIL:  ")[1])

    access_token = await JWT.create_token(user_id=user.id, timedelta=datetime.timedelta(seconds=config.ACCESS_TOKEN_EXPIRE))
    refresh_token = await JWT.create_token(user_id=user.id, timedelta=datetime.timedelta(seconds=config.REFRESH_TOKEN_EXPIRE))

    try:
        await Sessions.create_session(session, user_id=user.id, token=refresh_token)
    except IntegrityError:
        raise HTTPError(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="internal server error", error="bad session")

    response.set_cookie(
        key=config.REFRESH_TOKEN_KEY,
        value=refresh_token,
        max_age=config.REFRESH_TOKEN_EXPIRE,
        expires=config.REFRESH_TOKEN_EXPIRE,
        path="/",
        domain="",
        httponly=True,
        secure=False
    )

    return AccessTokenSchema(access_token=access_token)


@router.post("/signin", status_code=status.HTTP_200_OK)
async def signin_in_account(body: SigninSchema, response: Response, session: AsyncSession = Depends(get_session)) -> AccessTokenSchema:
    user = await Users.find_user(session, username=body.username, email=body.email)

    if not user:
        raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="username or email is not exist")

    current_session = await Sessions.find_session_by_user_id(session, user_id=user.id)
    if Hashlibrary.SHA256(body.password) != user.password:
        if current_session:
            await Sessions.delete_session(session, current_session=current_session)
        raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="check password again", error="password is not correctly")

    access_token = await JWT.create_token(user_id=user.id, timedelta=datetime.timedelta(seconds=config.ACCESS_TOKEN_EXPIRE))
    refresh_token = await JWT.create_token(user_id=user.id, timedelta=datetime.timedelta(seconds=config.REFRESH_TOKEN_EXPIRE))

    if current_session:
        await Sessions.update_session(session, current_session=current_session, token=refresh_token)
    await Sessions.create_session(session, user_id=user.id, token=refresh_token)

    response.set_cookie(
        key=config.REFRESH_TOKEN_KEY,
        value=refresh_token,
        max_age=config.REFRESH_TOKEN_EXPIRE,
        expires=config.REFRESH_TOKEN_EXPIRE,
        path="/",
        domain="",
        httponly=True,
        secure=False
    )

    return AccessTokenSchema(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_from_account(request: Request, response: Response, session: AsyncSession = Depends(get_session)):
    refresh_token = request.cookies.get(config.REFRESH_TOKEN_KEY)

    if refresh_token:
        response.delete_cookie(key=config.REFRESH_TOKEN_KEY)
        current_session = await Sessions.find_session(session, token=refresh_token)
        if current_session:
            await Sessions.delete_session(session, current_session)
        return HTTPSuccess(status=status.HTTP_200_OK, data="successful logout from account")

    raise HTTPError(status=status.HTTP_401_UNAUTHORIZED, message="you not authorized")

