import pytz
from envparse import env

TIMEZONE = env.str("TZ", default=pytz.timezone("Europe/Moscow"))
SECRET_KEY = env.str(
    "SECRET_KEY",
    default="02b69f5b9af44262e2f0128a7e88d1f85719a6d299efb7528517c9f26c1f452a",
)

ALGORITHM = env.str("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE = env.int("ACCESS_TOKEN_EXPIRE", default=30 * 60)
REFRESH_TOKEN_EXPIRE = env.int("REFRESH_TOKEN_EXPIRE", default=7 * 24 * 60 * 60)
REFRESH_TOKEN_KEY = env.str("REFRESH_TOKEN_KEY", default="refresh_token_key")

TITLE = env.str("TITLE", default="TITLE_EXAMPLE")
DESCRIPTION = env.str("DESCRIPTION", default="DESCRIPTION_EXAMPLE")
VERSION = env.str("VERSION", default="1.0.0")

DATABASE_URI = env.str("DATABASE_URI", default="postgresql+asyncpg://postgres:postgres@localhost/webtronics")
PASSWORD_SECRET_SALT = env.str("PASSWORD_SECRET_SALT", default="c3bc22e35913eceb003fbec8e07c45d981872e15cccbdf7e9b44d6c424f53177")
