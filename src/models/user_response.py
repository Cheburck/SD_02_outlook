from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    login: str
    firstName: str
    lastName: str
