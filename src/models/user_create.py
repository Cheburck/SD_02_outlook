from pydantic import BaseModel


class UserCreate(BaseModel):
    login: str
    firstName: str
    lastName: str
    password: str
