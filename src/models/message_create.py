from pydantic import BaseModel


class MessageCreate(BaseModel):
    subject: str
    body: str
    sender: str
    recipient: str
