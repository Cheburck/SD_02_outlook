from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserResponse(BaseModel):
    id: int
    login: str
    firstName: str
    lastName: str
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True
