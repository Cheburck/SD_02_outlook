from pydantic import BaseModel


class FolderCreate(BaseModel):
    name: str
    userId: int
