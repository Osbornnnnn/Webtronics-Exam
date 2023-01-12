from fastapi import HTTPException
from fastapi.responses import UJSONResponse
from pydantic import typing


class HTTPError(HTTPException):
    def __init__(self,
                 status: int,
                 message: str,
                 error: str | None = None,
                 headers: dict[str, str] | None = None
                 ):
        self.status_code = status
        if error is None:
            self.detail = {
                "message": message,
            }
        else:
            self.detail = {
                "message": message,
                "error": error
            }
        self.headers = headers


class HTTPSuccess(UJSONResponse):
    def __init__(self,
                 status: int,
                 data: typing.Any,
                 headers: dict[str, str] | None = None
                 ):
        super().__init__(status_code=status, content=data, headers=headers)
