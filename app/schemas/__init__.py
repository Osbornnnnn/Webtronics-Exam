from pydantic import BaseModel


class Model(BaseModel):
    class Config:
        orm_mode = True
