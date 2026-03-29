from fastapi import APIRouter, HTTPException, status

from models.message_create import MessageCreate
from models.message_response import MessageResponse
from database import db

router = APIRouter()


@router.post("/api/folders/{folder_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(folder_id: int, message_data: MessageCreate):
    try:
        message = db.create_message(
            folder_id=folder_id,
            subject=message_data.subject,
            body=message_data.body,
            sender=message_data.sender,
            recipient=message_data.recipient
        )
        return MessageResponse(
            id=message["id"], folderId=message["folderId"], subject=message["subject"],
            body=message["body"], sender=message["sender"], recipient=message["recipient"],
            createdAt=message["createdAt"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/folders/{folder_id}/messages", response_model=list[MessageResponse])
async def get_messages_in_folder(folder_id: int):
    folder = db.get_folder_by_id(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Folder with id {folder_id} not found")
    
    messages = db.get_messages_by_folder(folder_id)
    return [MessageResponse(
        id=m["id"], folderId=m["folderId"], subject=m["subject"],
        body=m["body"], sender=m["sender"], recipient=m["recipient"],
        createdAt=m["createdAt"]
    ) for m in messages]


@router.get("/api/messages/{message_id}", response_model=MessageResponse)
async def get_message_by_id(message_id: int):
    message = db.get_message_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail=f"Message with id {message_id} not found")
    return MessageResponse(
        id=message["id"], folderId=message["folderId"], subject=message["subject"],
        body=message["body"], sender=message["sender"], recipient=message["recipient"],
        createdAt=message["createdAt"]
    )
