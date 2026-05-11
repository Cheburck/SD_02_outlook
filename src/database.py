import asyncpg
import os
from typing import Dict, List, Optional
from datetime import datetime


class PostgresDatabase:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._initialized = False
    
    async def connect(self):
        if self._initialized:
            return
        
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/filestorage")
        
        try:
            self.pool = await asyncpg.create_pool(database_url)
            self._initialized = True
            print(f"Connected to database: {database_url}")
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self._initialized = False
    
    async def create_user(self, login: str, firstName: str, lastName: str, password_hash: str) -> dict:
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO users (login, first_name, last_name, password_hash)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id, login, first_name, last_name, created_at
                    """,
                    login, firstName, lastName, password_hash
                )
                return {
                    "id": row["id"],
                    "login": row["login"],
                    "firstName": row["first_name"],
                    "lastName": row["last_name"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
            except asyncpg.UniqueViolationError:
                raise ValueError(f"User with login '{login}' already exists")
    
    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, login, first_name, last_name, created_at FROM users WHERE id = $1",
                user_id
            )
            if row:
                return {
                    "id": row["id"],
                    "login": row["login"],
                    "firstName": row["first_name"],
                    "lastName": row["last_name"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
            return None
    
    async def get_user_by_login(self, login: str) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, login, first_name, last_name, password_hash, created_at FROM users WHERE login = $1",
                login
            )
            if row:
                return {
                    "id": row["id"],
                    "login": row["login"],
                    "firstName": row["first_name"],
                    "lastName": row["last_name"],
                    "password_hash": row["password_hash"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
            return None
    
    async def search_users_by_name(self, firstName: Optional[str] = None, lastName: Optional[str] = None) -> List[dict]:
        async with self.pool.acquire() as conn:
            query = "SELECT id, login, first_name, last_name, created_at FROM users WHERE 1=1"
            params = []
            param_count = 1
            
            if firstName:
                query += f" AND first_name ILIKE ${param_count}"
                params.append(f"%{firstName}%")
                param_count += 1
            
            if lastName:
                query += f" AND last_name ILIKE ${param_count}"
                params.append(f"%{lastName}%")
                param_count += 1
            
            rows = await conn.fetch(query, *params)
            return [
                {
                    "id": row["id"],
                    "login": row["login"],
                    "firstName": row["first_name"],
                    "lastName": row["last_name"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
                for row in rows
            ]
    
    async def create_folder(self, name: str, user_id: int) -> dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO folders (name, user_id)
                VALUES ($1, $2)
                RETURNING id, name, user_id, created_at
                """,
                name, user_id
            )
            return {
                "id": row["id"],
                "name": row["name"],
                "userId": row["user_id"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
    
    async def get_all_folders(self) -> List[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT id, name, user_id, created_at FROM folders ORDER BY id")
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "userId": row["user_id"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
                for row in rows
            ]
    
    async def get_folder_by_id(self, folder_id: int) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, user_id, created_at FROM folders WHERE id = $1",
                folder_id
            )
            if row:
                return {
                    "id": row["id"],
                    "name": row["name"],
                    "userId": row["user_id"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
            return None
    
    async def get_folders_by_user_id(self, user_id: int) -> List[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, name, user_id, created_at FROM folders WHERE user_id = $1 ORDER BY id",
                user_id
            )
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "userId": row["user_id"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
                for row in rows
            ]
    
    async def create_message(self, folder_id: int, subject: str, body: str, sender: str, recipient: str) -> dict:
        async with self.pool.acquire() as conn:
            folder_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM folders WHERE id = $1)", folder_id)
            if not folder_exists:
                raise ValueError(f"Folder with id {folder_id} not found")
            
            row = await conn.fetchrow(
                """
                INSERT INTO messages (folder_id, subject, body, sender, recipient)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, folder_id, subject, body, sender, recipient, created_at
                """,
                folder_id, subject, body, sender, recipient
            )
            return {
                "id": row["id"],
                "folderId": row["folder_id"],
                "subject": row["subject"],
                "body": row["body"],
                "sender": row["sender"],
                "recipient": row["recipient"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
    
    async def get_messages_by_folder(self, folder_id: int) -> List[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, folder_id, subject, body, sender, recipient, created_at FROM messages WHERE folder_id = $1 ORDER BY id",
                folder_id
            )
            return [
                {
                    "id": row["id"],
                    "folderId": row["folder_id"],
                    "subject": row["subject"],
                    "body": row["body"],
                    "sender": row["sender"],
                    "recipient": row["recipient"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
                for row in rows
            ]
    
    async def get_message_by_id(self, message_id: int) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, folder_id, subject, body, sender, recipient, created_at FROM messages WHERE id = $1",
                message_id
            )
            if row:
                return {
                    "id": row["id"],
                    "folderId": row["folder_id"],
                    "subject": row["subject"],
                    "body": row["body"],
                    "sender": row["sender"],
                    "recipient": row["recipient"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
            return None
    
    async def get_message_by_subject(self, subject: str) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, folder_id, subject, body, sender, recipient, created_at FROM messages WHERE subject = $1",
                subject
            )
            if row:
                return {
                    "id": row["id"],
                    "folderId": row["folder_id"],
                    "subject": row["subject"],
                    "body": row["body"],
                    "sender": row["sender"],
                    "recipient": row["recipient"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
            return None
    
    async def delete_message(self, message_id: int) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM messages WHERE id = $1", message_id)
            return result == "DELETE 1"
    
    async def delete_folder(self, folder_id: int) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM folders WHERE id = $1", folder_id)
            return result == "DELETE 1"


db = PostgresDatabase()
