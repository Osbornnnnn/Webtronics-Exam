from . import Model


class UserResponseSchema(Model):
    full_name: str
    username: str
    email: str
