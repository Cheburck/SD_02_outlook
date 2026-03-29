from pydantic import BaseModel


class FolderResponse(BaseModel):
    id: int
    name: str
    userId: int
