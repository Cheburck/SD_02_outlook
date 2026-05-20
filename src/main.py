# Основное приложение FastAPI для Email системы
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Подключение к MongoDB при запуске
    await db.connect()
    print("Connected to MongoDB")
    yield
    # Отключение от MongoDB при остановке
    await db.disconnect()
    print("Disconnected from MongoDB")


app = FastAPI(title="Email REST API", version="1.0.0", lifespan=lifespan)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"status": "healthy", "database": "mongodb"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
