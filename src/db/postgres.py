"""
PostgreSQL database connection and operations for Email System.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
from datetime import datetime


class Database:
    """PostgreSQL database handler for Email System."""
    
    def __init__(self, connection):
        self.conn = connection
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, login: str, password_hash: str, first_name: str, last_name: str) -> Dict[str, Any]:
        """Create a new user."""
        query = """
            INSERT INTO users (login, password_hash, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            RETURNING id, login, first_name, last_name, created_at
        """
        self.cursor.execute(query, (login, password_hash, first_name, last_name))
        self.conn.commit()
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        query = """
            SELECT id, login, first_name, last_name, created_at
            FROM users
            WHERE id = %s
        """
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_user_by_login(self, login: str) -> Optional[Dict[str, Any]]:
        """Get user by login."""
        query = """
            SELECT id, login, first_name, last_name, password_hash, created_at
            FROM users
            WHERE login = %s
        """
        self.cursor.execute(query, (login,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def search_users_by_name(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search users by name mask."""
        conditions = []
        params = []
        
        if first_name:
            conditions.append("first_name ILIKE %s")
            params.append(f"%{first_name}%")
        if last_name:
            conditions.append("last_name ILIKE %s")
            params.append(f"%{last_name}%")
        
        if not conditions:
            return []
        
        query = f"""
            SELECT id, login, first_name, last_name, created_at
            FROM users
            WHERE {' OR '.join(conditions)}
            ORDER BY last_name, first_name
        """
        self.cursor.execute(query, tuple(params))
        results = self.cursor.fetchall()
        return [dict(row) for row in results]
    
    def user_exists_by_login(self, login: str) -> bool:
        """Check if user with given login exists."""
        query = "SELECT 1 FROM users WHERE login = %s LIMIT 1"
        self.cursor.execute(query, (login,))
        return self.cursor.fetchone() is not None
    
    # ==================== FOLDER OPERATIONS ====================
    
    def create_folder(self, name: str, user_id: int) -> Dict[str, Any]:
        """Create a new folder."""
        query = """
            INSERT INTO folders (name, user_id)
            VALUES (%s, %s)
            RETURNING id, name, user_id, created_at
        """
        self.cursor.execute(query, (name, user_id))
        self.conn.commit()
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_all_folders(self) -> List[Dict[str, Any]]:
        """Get all folders."""
        query = """
            SELECT id, name, user_id, created_at
            FROM folders
            ORDER BY id
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [dict(row) for row in results]
    
    def get_folders_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all folders for a specific user."""
        query = """
            SELECT id, name, user_id, created_at
            FROM folders
            WHERE user_id = %s
            ORDER BY id
        """
        self.cursor.execute(query, (user_id,))
        results = self.cursor.fetchall()
        return [dict(row) for row in results]
    
    def get_folder_by_id(self, folder_id: int) -> Optional[Dict[str, Any]]:
        """Get folder by ID."""
        query = """
            SELECT id, name, user_id, created_at
            FROM folders
            WHERE id = %s
        """
        self.cursor.execute(query, (folder_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    # ==================== MESSAGE OPERATIONS ====================
    
    def create_message(self, folder_id: int, subject: str, body: str, sender: str, recipient: str) -> Dict[str, Any]:
        """Create a new message."""
        query = """
            INSERT INTO messages (folder_id, subject, body, sender, recipient)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, folder_id, subject, body, sender, recipient, created_at
        """
        self.cursor.execute(query, (folder_id, subject, body, sender, recipient))
        self.conn.commit()
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_messages_by_folder(self, folder_id: int) -> List[Dict[str, Any]]:
        """Get all messages in a folder."""
        query = """
            SELECT id, folder_id, subject, body, sender, recipient, created_at
            FROM messages
            WHERE folder_id = %s
            ORDER BY created_at DESC
        """
        self.cursor.execute(query, (folder_id,))
        results = self.cursor.fetchall()
        return [dict(row) for row in results]
    
    def get_message_by_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Get message by ID."""
        query = """
            SELECT id, folder_id, subject, body, sender, recipient, created_at
            FROM messages
            WHERE id = %s
        """
        self.cursor.execute(query, (message_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None


def get_db_connection() -> Database:
    """
    Create and return a database connection.
    
    Environment variables:
    - DATABASE_URL: PostgreSQL connection string
    - DB_HOST: Database host (default: localhost)
    - DB_PORT: Database port (default: 5432)
    - DB_NAME: Database name (default: outlook_db)
    - DB_USER: Database user (default: postgres)
    - DB_PASSWORD: Database password (default: postgres)
    """
    
    # Try to get connection from DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Parse DATABASE_URL (postgresql://user:pass@host:port/dbname)
        conn = psycopg2.connect(database_url)
    else:
        # Use individual parameters
        host = os.environ.get('DB_HOST', 'localhost')
        port = os.environ.get('DB_PORT', '5432')
        dbname = os.environ.get('DB_NAME', 'outlook_db')
        user = os.environ.get('DB_USER', 'postgres')
        password = os.environ.get('DB_PASSWORD', 'postgres')
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
    
    return Database(conn)
