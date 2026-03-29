from pydantic import BaseModel
from datetime import datetime


class MessageResponse(BaseModel):
    id: int
    folderId: int
    subject: str
    body: str
    sender: str
    recipient: str
    createdAt: datetime
