from fastapi import APIRouter, HTTPException, status, Depends, Request
from datetime import datetime

from models.folder_create import FolderCreate
from models.folder_response import FolderResponse
from db.postgres import get_db_connection, Database
from cache import cache
from rate_limiter import limiter, RATE_LIMITS
from events.events import FolderCreated
from events.publisher import get_publisher
from events.config import RabbitMQConfig

router = APIRouter()


def get_db() -> Database:
    """Dependency to get database connection."""
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()


@router.post("/api/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMITS['folder_create'])
async def create_folder(folder_data: FolderCreate, request: Request, db: Database = Depends(get_db)):
    # Check if user exists
    if not db.get_user_by_id(folder_data.userId):
        raise HTTPException(status_code=404, detail=f"User with id {folder_data.userId} not found")
    
    folder = db.create_folder(
        name=folder_data.name,
        user_id=folder_data.userId
    )
    
    # Invalidate user folders cache
    cache.invalidate_user(folder_data.userId)
    
    # Publish FolderCreated event
    publisher = get_publisher()
    if publisher:
        event = FolderCreated(
            folder_id=folder["id"],
            name=folder["name"],
            user_id=folder["user_id"],
            created_at=folder["created_at"],
        )
        publisher.publish(event, RabbitMQConfig.ROUTING_FOLDER_CREATED)
    
    return FolderResponse(
        id=folder["id"],
        name=folder["name"],
        userId=folder["user_id"],
        createdAt=folder["created_at"]
    )


@router.get("/api/folders", response_model=list[FolderResponse])
@limiter.limit(RATE_LIMITS['read'])
async def get_all_folders(request: Request, db: Database = Depends(get_db)):
    # Try to get from cache (all folders)
    cache_key = "folders:all"
    cached_folders = cache.get(cache_key)
    if cached_folders:
        return [FolderResponse(**f) for f in cached_folders]
    
    # Get from database
    folders = db.get_all_folders()
    folders_data = [
        {
            "id": f["id"],
            "name": f["name"],
            "userId": f["user_id"],
            "createdAt": f["created_at"]
        }
        for f in folders
    ]
    
    # Cache the result
    cache.set(cache_key, folders_data, ttl=60)
    
    return [FolderResponse(**f) for f in folders_data]


@router.get("/api/users/{user_id}/folders", response_model=list[FolderResponse])
@limiter.limit(RATE_LIMITS['read'])
async def get_user_folders(user_id: int, request: Request, db: Database = Depends(get_db)):
    # Try to get from cache
    cache_key = f"user:{user_id}:folders"
    cached_folders = cache.get(cache_key)
    if cached_folders:
        return [FolderResponse(**f) for f in cached_folders]
    
    # Get from database
    folders = db.get_folders_by_user(user_id)
    folders_data = [
        {
            "id": f["id"],
            "name": f["name"],
            "userId": f["user_id"],
            "createdAt": f["created_at"]
        }
        for f in folders
    ]
    
    # Cache the result
    cache.set(cache_key, folders_data, ttl=300)
    
    return [FolderResponse(**f) for f in folders_data]
