# Основное приложение FastAPI для Email системы
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from rate_limiter import limiter, rate_limit_exceeded_handler, RateLimitHeadersMiddleware
from cache import cache

app = FastAPI(title="Email REST API", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем rate limiting middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Добавляем middleware для rate limit заголовков
app.add_middleware(RateLimitHeadersMiddleware)

# Добавляем обработчик превышения rate limit
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Подключаем роуты
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.folders import router as folders_router
from routes.messages import router as messages_router

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(folders_router)
app.include_router(messages_router)


# Health check
@app.get("/health")
async def health_check():
    redis_status = "connected" if cache.is_connected() else "disconnected"
    return {
        "status": "healthy",
        "cache": redis_status
    }


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения."""
    if cache.is_connected():
        print("✓ Redis cache connected")
    else:
        print("⚠ Redis cache not available, running without caching")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
