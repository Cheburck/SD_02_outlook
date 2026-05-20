from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FolderResponse(BaseModel):
    id: int
    name: str
    userId: int
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True
