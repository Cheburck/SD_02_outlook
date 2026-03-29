from fastapi import APIRouter, HTTPException, Depends, status

from models.folder_create import FolderCreate
from models.folder_response import FolderResponse
from database import db
from auth import get_current_user

router = APIRouter()


@router.post("/api/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(folder_data: FolderCreate, current_user: dict = Depends(get_current_user)):
    user = db.get_user_by_id(folder_data.userId)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {folder_data.userId} not found")
    
    folder = db.create_folder(name=folder_data.name, user_id=folder_data.userId)
    return FolderResponse(id=folder["id"], name=folder["name"], userId=folder["userId"])


@router.get("/api/folders", response_model=list[FolderResponse])
async def get_all_folders(current_user: dict = Depends(get_current_user)):
    folders = db.get_all_folders()
    return [FolderResponse(id=f["id"], name=f["name"], userId=f["userId"]) for f in folders]
