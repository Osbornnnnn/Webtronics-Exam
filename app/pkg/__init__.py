from .cryptography import JWT, Hashlibrary
from .. import config

JWT = JWT(secret_key=config.SECRET_KEY, algorithm=config.ALGORITHM)
Hashlibrary = Hashlibrary(password_salt=config.PASSWORD_SECRET_SALT)
