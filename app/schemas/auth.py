from . import Model


class AccessTokenSchema(Model):
    access_token: str


class SignupSchema(Model):
    full_name: str
    username: str
    email: str
    password: str


class SigninSchema(Model):
    username: str = None
    email: str = None
    password: str
