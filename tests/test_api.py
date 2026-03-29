import pytest
import os

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealth:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestAuth:
    def test_register_user(self):
        user_data = {
            "login": "testuser",
            "firstName": "Test",
            "lastName": "User",
            "password": "password123"
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_user(self):
        user_data = {
            "login": "duplicateuser",
            "firstName": "Duplicate",
            "lastName": "User",
            "password": "password123"
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 200
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_login_success(self):
        user_data = {
            "login": "loginuser",
            "firstName": "Login",
            "lastName": "User",
            "password": "password123"
        }
        client.post("/api/auth/register", json=user_data)
        response = client.post("/api/auth/login", json={
            "login": "loginuser",
            "password": "password123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid_credentials(self):
        response = client.post("/api/auth/login", json={
            "login": "nonexistent",
            "password": "wrongpassword"
        })
        assert response.status_code == 401


class TestUsers:
    def test_create_user(self):
        user_data = {
            "login": "newuser",
            "firstName": "New",
            "lastName": "User",
            "password": "password123"
        }
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["login"] == "newuser"
        assert data["firstName"] == "New"
        assert data["lastName"] == "User"
        assert "id" in data
    
    def test_get_user_by_login(self):
        user_data = {
            "login": "findme",
            "firstName": "Find",
            "lastName": "Me",
            "password": "password123"
        }
        client.post("/api/users", json=user_data)
        response = client.get("/api/users/login/findme")
        assert response.status_code == 200
        data = response.json()
        assert data["login"] == "findme"
    
    def test_get_user_by_login_not_found(self):
        response = client.get("/api/users/login/nonexistent")
        assert response.status_code == 404
    
    def test_search_users_by_name(self):
        users = [
            {"login": "john_doe", "firstName": "John", "lastName": "Doe", "password": "pass123"},
            {"login": "jane_doe", "firstName": "Jane", "lastName": "Doe", "password": "pass123"},
            {"login": "john_smith", "firstName": "John", "lastName": "Smith", "password": "pass123"},
        ]
        for user in users:
            client.post("/api/users", json=user)
        
        response = client.get("/api/users/search?firstName=John")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        
        response = client.get("/api/users/search?lastName=Doe")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        
        response = client.get("/api/users/search?firstName=John&lastName=Doe")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_search_users_no_params(self):
        response = client.get("/api/users/search")
        assert response.status_code == 400


class TestFolders:
    def get_auth_token(self):
        user_data = {
            "login": f"folderuser_{os.urandom(4).hex()}",
            "firstName": "Folder",
            "lastName": "User",
            "password": "password123"
        }
        response = client.post("/api/auth/register", json=user_data)
        return response.json()["access_token"]
    
    def test_create_folder_protected(self):
        folder_data = {"name": "Inbox", "userId": 1}
        response = client.post("/api/folders", json=folder_data)
        assert response.status_code == 401
    
    def test_create_folder_success(self):
        token = self.get_auth_token()
        user_data = {
            "login": f"owner_{os.urandom(4).hex()}",
            "firstName": "Owner",
            "lastName": "User",
            "password": "password123"
        }
        user_response = client.post("/api/users", json=user_data)
        user_id = user_response.json()["id"]
        
        folder_data = {"name": "Inbox", "userId": user_id}
        response = client.post("/api/folders", json=folder_data, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201
        assert response.json()["name"] == "Inbox"
    
    def test_get_all_folders_protected(self):
        response = client.get("/api/folders")
        assert response.status_code == 401
    
    def test_get_all_folders_success(self):
        token = self.get_auth_token()
        user_data = {
            "login": f"folderowner_{os.urandom(4).hex()}",
            "firstName": "Folder",
            "lastName": "Owner",
            "password": "password123"
        }
        user_response = client.post("/api/users", json=user_data)
        user_id = user_response.json()["id"]
        
        for name in ["Inbox", "Sent", "Drafts"]:
            client.post("/api/folders", json={"name": name, "userId": user_id}, headers={"Authorization": f"Bearer {token}"})
        
        response = client.get("/api/folders", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert len(response.json()) >= 3


class TestMessages:
    def setup_message_test(self):
        user_data = {
            "login": f"msguser_{os.urandom(4).hex()}",
            "firstName": "Message",
            "lastName": "User",
            "password": "password123"
        }
        auth_response = client.post("/api/auth/register", json=user_data)
        token = auth_response.json()["access_token"]
        
        folder_response = client.post("/api/folders", json={"name": "Inbox", "userId": 1}, headers={"Authorization": f"Bearer {token}"})
        folder_id = folder_response.json()["id"]
        return token, folder_id
    
    def test_create_message(self):
        token, folder_id = self.setup_message_test()
        message_data = {
            "subject": "Test Subject",
            "body": "Test message body",
            "sender": "sender@example.com",
            "recipient": "recipient@example.com"
        }
        response = client.post(f"/api/folders/{folder_id}/messages", json=message_data)
        assert response.status_code == 201
        data = response.json()
        assert data["subject"] == "Test Subject"
        assert data["folderId"] == folder_id
    
    def test_create_message_folder_not_found(self):
        token, _ = self.setup_message_test()
        message_data = {
            "subject": "Test",
            "body": "Test",
            "sender": "test@test.com",
            "recipient": "test@test.com"
        }
        response = client.post("/api/folders/99999/messages", json=message_data)
        assert response.status_code == 404
    
    def test_get_messages_in_folder(self):
        token, folder_id = self.setup_message_test()
        for i in range(3):
            client.post(f"/api/folders/{folder_id}/messages", json={
                "subject": f"Message {i}",
                "body": f"Body {i}",
                "sender": f"sender{i}@example.com",
                "recipient": f"recipient{i}@example.com"
            })
        
        response = client.get(f"/api/folders/{folder_id}/messages")
        assert response.status_code == 200
        assert len(response.json()) == 3
    
    def test_get_message_by_id(self):
        token, folder_id = self.setup_message_test()
        create_response = client.post(f"/api/folders/{folder_id}/messages", json={
            "subject": "Find Me",
            "body": "Find this message",
            "sender": "sender@example.com",
            "recipient": "recipient@example.com"
        })
        message_id = create_response.json()["id"]
        
        response = client.get(f"/api/messages/{message_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["subject"] == "Find Me"
    
    def test_get_message_not_found(self):
        response = client.get("/api/messages/99999")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
