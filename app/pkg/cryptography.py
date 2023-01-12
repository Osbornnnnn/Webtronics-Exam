import datetime
import hashlib

import jwt

from ..schemas import Model


class PayloadSchema(Model):
    user_id: int
    exp: datetime.datetime

class JWT:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def _encode(self, payload: PayloadSchema) -> str:
        return jwt.encode(payload=payload.dict(), key=self.secret_key, algorithm=self.algorithm)

    async def _decode(self, token: str) -> PayloadSchema:
        return PayloadSchema(**jwt.decode(jwt=token, key=self.secret_key, algorithms=[self.algorithm]))

    async def create_token(self, user_id: str, timedelta: datetime.timedelta = datetime.timedelta(minutes=30)) -> str:
        payload = PayloadSchema(
            user_id=user_id,
            exp=datetime.datetime.utcnow() + timedelta
        )

        return await self._encode(payload)

    async def verify_token(self, token: str) -> PayloadSchema:
        payload = await self._decode(token)
        # custom errors
        return payload

    class ExpiredSignatureError(jwt.exceptions.ExpiredSignatureError):
        pass

    class InvalidSignatureError(jwt.exceptions.InvalidSignatureError):
        pass

    class DecodeError(jwt.exceptions.DecodeError):
        pass


class Hashlibrary:
    def __init__(self, password_salt: str):
        self.password_salt = password_salt

    def SHA256(self, data: str | bytes) -> str:
        if isinstance(data, str):
            return hashlib.sha3_256(data.encode()).hexdigest()
        return hashlib.sha3_256(data).hexdigest()
