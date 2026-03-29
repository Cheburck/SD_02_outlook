from fastapi import APIRouter, HTTPException, status
from passlib.hash import sha256_crypt

from models.user_create import UserCreate
from models.user_login import UserLogin
from models.token_response import TokenResponse
from database import db
from auth import create_access_token

router = APIRouter()


@router.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    try:
        password_hash = sha256_crypt.hash(user_data.password)
        user = db.create_user(
            login=user_data.login,
            firstName=user_data.firstName,
            lastName=user_data.lastName,
            password_hash=password_hash
        )
        access_token = create_access_token(data={"sub": str(user["id"]), "login": user["login"]})
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = db.get_user_by_login(credentials.login)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or password")
    
    if not sha256_crypt.verify(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or password")
    
    return {"access_token": create_access_token(data={"sub": str(user["id"]), "login": user["login"]}), "token_type": "bearer"}
