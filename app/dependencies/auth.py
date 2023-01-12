import jwt
from fastapi import Request, status
from fastapi.openapi.models import HTTPBase as HTTPBaseModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param

from ..pkg import JWT
from ..pkg.cryptography import PayloadSchema
from ..responses import HTTPError


class HTTPBearerScheme(SecurityBase):
    def __init__(
        self,
        *,
        scheme_name: str | None = None,
        description: str | None = None,
    ):
        self.model = HTTPBaseModel(scheme="bearer", description=description)
        self.scheme_name = scheme_name or self.__class__.__name__

    async def __call__(self, request: Request) -> PayloadSchema | None:
        authorization = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise HTTPError(
                status=status.HTTP_401_UNAUTHORIZED,
                message="not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = await JWT.verify_token(token)
        except jwt.exceptions.ExpiredSignatureError as e:
            raise HTTPError(
                status=status.HTTP_401_UNAUTHORIZED, message="access token expired", error=e.__str__(), headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.exceptions.InvalidSignatureError as e:
            raise HTTPError(
                status=status.HTTP_401_UNAUTHORIZED, message="invalid access token", error=e.__str__(), headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.exceptions.DecodeError as e:
            raise HTTPError(
                status=status.HTTP_401_UNAUTHORIZED, message="invalid access token", error=e.__str__(), headers={"WWW-Authenticate": "Bearer"}
            )

        return payload
