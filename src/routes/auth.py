from fastapi import APIRouter, HTTPException, status, Depends, Request
from datetime import datetime

from models.user_login import UserLogin
from models.user_create import UserCreate
from models.token_response import TokenResponse
from models.user_response import UserResponse
from db.postgres import get_db_connection, Database
from cache import cache
from rate_limiter import limiter, RATE_LIMITS
from auth import create_access_token
from passlib.hash import sha256_crypt
from events.events import UserCreated
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


@router.post("/api/auth/login", response_model=TokenResponse)
@limiter.limit(RATE_LIMITS['auth_login'])
async def login(login_data: UserLogin, request: Request, db: Database = Depends(get_db)):
    # Try to get user from cache
    cache_key = f"user:login:{login_data.login}"
    user = cache.get(cache_key)
    
    if not user:
        # Get from database
        user = db.get_user_by_login(login_data.login)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Cache user data (with password_hash for verification)
        user_data = {
            "id": user["id"],
            "login": user["login"],
            "firstName": user["first_name"],
            "lastName": user["last_name"],
            "password_hash": user["password_hash"]
        }
        cache.set(cache_key, user_data, ttl=60)
    
    # Verify password
    if not sha256_crypt.verify(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    token = create_access_token(data={"sub": user["login"], "user_id": user["id"]})
    
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMITS['auth_register'])
async def register(user_data: UserCreate, request: Request, db: Database = Depends(get_db)):
    # Check if user already exists
    if db.user_exists_by_login(user_data.login):
        raise HTTPException(status_code=400, detail=f"User with login '{user_data.login}' already exists")
    
    # Create user
    password_hash = sha256_crypt.hash(user_data.password)
    user = db.create_user(
        login=user_data.login,
        password_hash=password_hash,
        first_name=user_data.firstName,
        last_name=user_data.lastName
    )
    
    # Invalidate cache
    cache.invalidate_user(user['id'])
    
    # Publish UserCreated event
    publisher = get_publisher()
    if publisher:
        event = UserCreated(
            user_id=user["id"],
            login=user["login"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            created_at=user["created_at"],
        )
        publisher.publish(event, RabbitMQConfig.ROUTING_USER_CREATED)
    
    return UserResponse(
        id=user["id"],
        login=user["login"],
        firstName=user["first_name"],
        lastName=user["last_name"],
        createdAt=user["created_at"]
    )
