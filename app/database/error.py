from sqlalchemy.exc import IntegrityError

class DuplicateError(IntegrityError):
    pass
