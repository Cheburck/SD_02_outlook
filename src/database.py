# MongoDB Database Module for Email API
import os
from typing import Dict, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pymongo.errors import DuplicateKeyError


class MongoDB:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self._initialized = False
    
    async def connect(self):
        """Подключение к MongoDB"""
        if self._initialized:
            return
        
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        database_name = os.getenv("MONGODB_DATABASE", "email_db")
        
        self.client = AsyncIOMotorClient(mongodb_uri)
        self.db = self.client[database_name]
        
        # Создаём индексы
        await self._create_indexes()
        self._initialized = True
    
    async def disconnect(self):
        """Отключение от MongoDB"""
        if self.client:
            self.client.close()
            self._initialized = False
    
    async def _create_indexes(self):
        """Создание индексов для оптимизации запросов"""
        # Индексы для users
        await self.db.users.create_index("login", unique=True)
        await self.db.users.create_index([("firstName", 1), ("lastName", 1)])
        
        # Индексы для folders
        await self.db.folders.create_index("userId")
        
        # Индексы для messages
        await self.db.messages.create_index("folderId")
        await self.db.messages.create_index("createdAt", descending=True)
    
    # ==================== USER OPERATIONS ====================
    
    async def create_user(self, login: str, firstName: str, lastName: str, password_hash: str) -> dict:
        """Создание нового пользователя"""
        user = {
            "login": login,
            "firstName": firstName,
            "lastName": lastName,
            "password_hash": password_hash,
            "createdAt": datetime.utcnow()
        }
        
        try:
            result = await self.db.users.insert_one(user)
            user["_id"] = result.inserted_id
            return self._user_to_dict(user)
        except DuplicateKeyError:
            raise ValueError(f"User with login '{login}' already exists")
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Получение пользователя по ID"""
        try:
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            return self._user_to_dict(user) if user else None
        except Exception:
            return None
    
    async def get_user_by_login(self, login: str) -> Optional[dict]:
        """Получение пользователя по логину"""
        user = await self.db.users.find_one({"login": login})
        return self._user_to_dict(user) if user else None
    
    async def search_users_by_name(self, firstName: Optional[str] = None, lastName: Optional[str] = None) -> List[dict]:
        """Поиск пользователей по имени и/или фамилии"""
        query = {}
        
        if firstName:
            query["firstName"] = {"$regex": firstName, "$options": "i"}
        if lastName:
            query["lastName"] = {"$regex": lastName, "$options": "i"}
        
        users = await self.db.users.find(query).to_list(length=100)
        return [self._user_to_dict(u) for u in users]
    
    def _user_to_dict(self, user: dict) -> dict:
        """Преобразование документа пользователя в словарь"""
        if not user:
            return None
        return {
            "id": str(user["_id"]),
            "login": user["login"],
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "created_at": user.get("createdAt", datetime.utcnow()).isoformat() if isinstance(user.get("createdAt"), datetime) else user.get("createdAt")
        }
    
    # ==================== FOLDER OPERATIONS ====================
    
    async def create_folder(self, name: str, user_id: str) -> dict:
        """Создание новой папки"""
        # Проверяем существование пользователя
        user_exists = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user_exists:
            raise ValueError(f"User with id {user_id} not found")
        
        folder = {
            "name": name,
            "userId": ObjectId(user_id),
            "createdAt": datetime.utcnow()
        }
        
        result = await self.db.folders.insert_one(folder)
        folder["_id"] = result.inserted_id
        return self._folder_to_dict(folder)
    
    async def get_all_folders(self) -> List[dict]:
        """Получение всех папок"""
        folders = await self.db.folders.find().to_list(length=1000)
        return [self._folder_to_dict(f) for f in folders]
    
    async def get_folders_by_user(self, user_id: str) -> List[dict]:
        """Получение всех папок пользователя"""
        folders = await self.db.folders.find({"userId": ObjectId(user_id)}).to_list(length=1000)
        return [self._folder_to_dict(f) for f in folders]
    
    async def get_folder_by_id(self, folder_id: str) -> Optional[dict]:
        """Получение папки по ID"""
        try:
            folder = await self.db.folders.find_one({"_id": ObjectId(folder_id)})
            return self._folder_to_dict(folder) if folder else None
        except Exception:
            return None
    
    def _folder_to_dict(self, folder: dict) -> dict:
        """Преобразование документа папки в словарь"""
        if not folder:
            return None
        return {
            "id": str(folder["_id"]),
            "name": folder["name"],
            "userId": str(folder["userId"]),
            "created_at": folder.get("createdAt", datetime.utcnow()).isoformat() if isinstance(folder.get("createdAt"), datetime) else folder.get("createdAt")
        }
    
    # ==================== MESSAGE OPERATIONS ====================
    
    async def create_message(self, folder_id: str, subject: str, body: str, sender: str, recipient: str) -> dict:
        """Создание нового письма"""
        # Проверяем существование папки
        folder_exists = await self.db.folders.find_one({"_id": ObjectId(folder_id)})
        if not folder_exists:
            raise ValueError(f"Folder with id {folder_id} not found")
        
        message = {
            "folderId": ObjectId(folder_id),
            "subject": subject,
            "body": body,
            "sender": sender,
            "recipient": recipient,
            "createdAt": datetime.utcnow()
        }
        
        result = await self.db.messages.insert_one(message)
        message["_id"] = result.inserted_id
        return self._message_to_dict(message)
    
    async def get_messages_by_folder(self, folder_id: str) -> List[dict]:
        """Получение всех писем в папке"""
        messages = await self.db.messages.find(
            {"folderId": ObjectId(folder_id)}
        ).sort("createdAt", -1).to_list(length=1000)
        
        return [self._message_to_dict(m) for m in messages]
    
    async def get_message_by_id(self, message_id: str) -> Optional[dict]:
        """Получение письма по ID"""
        try:
            message = await self.db.messages.find_one({"_id": ObjectId(message_id)})
            return self._message_to_dict(message) if message else None
        except Exception:
            return None
    
    def _message_to_dict(self, message: dict) -> dict:
        """Преобразование документа письма в словарь"""
        if not message:
            return None
        return {
            "id": str(message["_id"]),
            "folderId": str(message["folderId"]),
            "subject": message["subject"],
            "body": message["body"],
            "sender": message["sender"],
            "recipient": message["recipient"],
            "createdAt": message.get("createdAt", datetime.utcnow()).isoformat() if isinstance(message.get("createdAt"), datetime) else message.get("createdAt")
        }


# Глобальный экземпляр базы данных
db = MongoDB()
