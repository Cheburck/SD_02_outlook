from fastapi import APIRouter, HTTPException, status, Depends

from models.message_create import MessageCreate
from models.message_response import MessageResponse
from db.postgres import get_db_connection, Database
from cache import cache
from rate_limiter import limiter, RATE_LIMITS

router = APIRouter()


def get_db() -> Database:
    """Dependency to get database connection."""
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()


@router.post("/api/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMITS['message_create'])
async def create_message(request, message_data: MessageCreate, db: Database = Depends(get_db)):
    # Check if folder exists
    if not db.get_folder_by_id(message_data.folderId):
        raise HTTPException(status_code=404, detail=f"Folder with id {message_data.folderId} not found")
    
    message = db.create_message(
        subject=message_data.subject,
        body=message_data.body,
        sender=message_data.sender,
        recipient=message_data.recipient,
        folder_id=message_data.folderId
    )
    
    # Invalidate folder messages cache
    cache.invalidate_folder(message_data.folderId)
    
    return MessageResponse(
        id=message["id"],
        folderId=message["folder_id"],
        subject=message["subject"],
        body=message["body"],
        sender=message["sender"],
        recipient=message["recipient"],
        createdAt=message["created_at"]
    )


@router.get("/api/folders/{folder_id}/messages", response_model=list[MessageResponse])
@limiter.limit(RATE_LIMITS['read'])
async def get_messages_in_folder(request, folder_id: int, db: Database = Depends(get_db)):
    # Try to get from cache
    cache_key = f"folder:{folder_id}:messages"
    cached_messages = cache.get(cache_key)
    if cached_messages:
        return [MessageResponse(**m) for m in cached_messages]
    
    # Get from database
    messages = db.get_messages_by_folder(folder_id)
    messages_data = [
        {
            "id": m["id"],
            "folderId": m["folder_id"],
            "subject": m["subject"],
            "body": m["body"],
            "sender": m["sender"],
            "recipient": m["recipient"],
            "createdAt": m["created_at"]
        }
        for m in messages
    ]
    
    # Cache the result
    cache.set(cache_key, messages_data, ttl=60)
    
    return [MessageResponse(**m) for m in messages_data]


@router.get("/api/messages/{message_id}", response_model=MessageResponse)
@limiter.limit(RATE_LIMITS['read'])
async def get_message(request, message_id: int, db: Database = Depends(get_db)):
    # Try to get from cache
    cache_key = f"message:{message_id}"
    cached_message = cache.get(cache_key)
    if cached_message:
        return MessageResponse(**cached_message)
    
    # Get from database
    message = db.get_message_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail=f"Message with id {message_id} not found")
    
    # Cache the result
    message_data = {
        "id": message["id"],
        "folderId": message["folder_id"],
        "subject": message["subject"],
        "body": message["body"],
        "sender": message["sender"],
        "recipient": message["recipient"],
        "createdAt": message["created_at"]
    }
    cache.set(cache_key, message_data, ttl=120)
    
    return MessageResponse(**message_data)
