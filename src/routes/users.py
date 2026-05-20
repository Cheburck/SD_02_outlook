from fastapi import APIRouter, HTTPException, status, Depends, Request

from models.user_create import UserCreate
from models.user_response import UserResponse
from db.postgres import get_db_connection, Database
from cache import cache
from rate_limiter import limiter, RATE_LIMITS
from passlib.hash import sha256_crypt

router = APIRouter()


def get_db() -> Database:
    """Dependency to get database connection."""
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()


@router.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMITS['user_create'])
async def create_user(user_data: UserCreate, request: Request, db: Database = Depends(get_db)):
    """
    Create a new user (admin endpoint).
    Note: Use /api/auth/register for self-registration.
    """
    # Check if user already exists
    if db.user_exists_by_login(user_data.login):
        raise HTTPException(status_code=400, detail=f"User with login '{user_data.login}' already exists")
    
    password_hash = sha256_crypt.hash(user_data.password)
    user = db.create_user(
        login=user_data.login,
        password_hash=password_hash,
        first_name=user_data.firstName,
        last_name=user_data.lastName
    )
    
    # Invalidate user cache
    cache.invalidate_user(user['id'])
    
    return UserResponse(
        id=user["id"],
        login=user["login"],
        firstName=user["first_name"],
        lastName=user["last_name"],
        createdAt=user["created_at"]
    )


@router.get("/api/users/login/{login}", response_model=UserResponse)
@limiter.limit(RATE_LIMITS['read'])
async def get_user_by_login(login: str, request: Request, db: Database = Depends(get_db)):
    # Try to get from cache
    cache_key = f"user:login:{login}"
    cached_user = cache.get(cache_key)
    if cached_user:
        return UserResponse(**cached_user)
    
    # Get from database
    user = db.get_user_by_login(login)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with login '{login}' not found")
    
    # Cache the result
    user_data = {
        "id": user["id"],
        "login": user["login"],
        "firstName": user["first_name"],
        "lastName": user["last_name"],
        "createdAt": user["created_at"]
    }
    cache.set(cache_key, user_data, ttl=300)
    
    return UserResponse(**user_data)


@router.get("/api/users/search", response_model=list[UserResponse])
@limiter.limit(RATE_LIMITS['user_search'])
async def search_users(firstName: str = None, lastName: str = None, request: Request = None, db: Database = Depends(get_db)):
    if not firstName and not lastName:
        raise HTTPException(status_code=400, detail="At least one of firstName or lastName must be provided")
    
    # Try to get from cache
    cache_key = f"user:search:firstName={firstName or ''}:lastName={lastName or ''}"
    cached_users = cache.get(cache_key)
    if cached_users:
        return [UserResponse(**u) for u in cached_users]
    
    # Get from database
    users = db.search_users_by_name(firstName, lastName)
    users_data = [
        {
            "id": u["id"],
            "login": u["login"],
            "firstName": u["first_name"],
            "lastName": u["last_name"],
            "createdAt": u["created_at"]
        }
        for u in users
    ]
    
    # Cache the result
    cache.set(cache_key, users_data, ttl=60)
    
    return [UserResponse(**u) for u in users_data]
