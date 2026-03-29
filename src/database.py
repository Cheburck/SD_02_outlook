from typing import Dict, List, Optional
from datetime import datetime


class InMemoryDatabase:
    def __init__(self):
        self._user_counter = 0
        self._folder_counter = 0
        self._message_counter = 0
        self.users: Dict[int, dict] = {}
        self.folders: Dict[int, dict] = {}
        self.messages: Dict[int, dict] = {}
        self.login_index: Dict[str, int] = {}
    
    def create_user(self, login: str, firstName: str, lastName: str, password_hash: str) -> dict:
        if login in self.login_index:
            raise ValueError(f"User with login '{login}' already exists")
        self._user_counter += 1
        user = {
            "id": self._user_counter,
            "login": login,
            "firstName": firstName,
            "lastName": lastName,
            "password_hash": password_hash,
            "created_at": datetime.now().isoformat()
        }
        self.users[self._user_counter] = user
        self.login_index[login] = self._user_counter
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        return self.users.get(user_id)
    
    def get_user_by_login(self, login: str) -> Optional[dict]:
        uid = self.login_index.get(login)
        return self.users.get(uid) if uid else None
    
    def search_users_by_name(self, firstName: Optional[str] = None, lastName: Optional[str] = None) -> List[dict]:
        results = []
        for user in self.users.values():
            match = True
            if firstName and firstName.lower() not in user["firstName"].lower():
                match = False
            if lastName and lastName.lower() not in user["lastName"].lower():
                match = False
            if match:
                results.append(user)
        return results
    
    def create_folder(self, name: str, user_id: int) -> dict:
        self._folder_counter += 1
        folder = {
            "id": self._folder_counter,
            "name": name,
            "userId": user_id,
            "created_at": datetime.now().isoformat()
        }
        self.folders[self._folder_counter] = folder
        return folder
    
    def get_all_folders(self) -> List[dict]:
        return list(self.folders.values())
    
    def get_folder_by_id(self, folder_id: int) -> Optional[dict]:
        return self.folders.get(folder_id)
    
    def create_message(self, folder_id: int, subject: str, body: str, sender: str, recipient: str) -> dict:
        if not self.get_folder_by_id(folder_id):
            raise ValueError(f"Folder with id {folder_id} not found")
        self._message_counter += 1
        message = {
            "id": self._message_counter,
            "folderId": folder_id,
            "subject": subject,
            "body": body,
            "sender": sender,
            "recipient": recipient,
            "createdAt": datetime.now().isoformat()
        }
        self.messages[self._message_counter] = message
        return message
    
    def get_messages_by_folder(self, folder_id: int) -> List[dict]:
        return [m for m in self.messages.values() if m["folderId"] == folder_id]
    
    def get_message_by_id(self, message_id: int) -> Optional[dict]:
        return self.messages.get(message_id)


db = InMemoryDatabase()
