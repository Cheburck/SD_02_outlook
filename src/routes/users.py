from fastapi import APIRouter, HTTPException, status

from models.user_create import UserCreate
from models.user_response import UserResponse
from database import db
from passlib.hash import sha256_crypt

router = APIRouter()


@router.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    password_hash = sha256_crypt.hash(user_data.password)
    user = db.create_user(
        login=user_data.login,
        firstName=user_data.firstName,
        lastName=user_data.lastName,
        password_hash=password_hash
    )
    return UserResponse(id=user["id"], login=user["login"], firstName=user["firstName"], lastName=user["lastName"])


@router.get("/api/users/login/{login}", response_model=UserResponse)
async def get_user_by_login(login: str):
    user = db.get_user_by_login(login)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with login '{login}' not found")
    return UserResponse(id=user["id"], login=user["login"], firstName=user["firstName"], lastName=user["lastName"])


@router.get("/api/users/search", response_model=list[UserResponse])
async def search_users(firstName: str = None, lastName: str = None):
    if not firstName and not lastName:
        raise HTTPException(status_code=400, detail="At least one of firstName or lastName must be provided")
    
    users = db.search_users_by_name(firstName, lastName)
    return [UserResponse(id=u["id"], login=u["login"], firstName=u["firstName"], lastName=u["lastName"]) for u in users]
