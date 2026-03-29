# Email REST API (Outlook)

REST API для управления почтой. Курс "Архитектура программных систем".

## Сущности

- **Folder** - почтовая папка
- **Message** - письмо
- **User** - пользователь

## Endpoints

| Метод | Endpoint | Auth |
|-------|----------|------|
| POST | `/api/auth/register` | - |
| POST | `/api/auth/login` | - |
| POST | `/api/users` | - |
| GET | `/api/users/login/{login}` | - |
| GET | `/api/users/search` | - |
| POST | `/api/folders` | + |
| GET | `/api/folders` | + |
| POST | `/api/folders/{folder_id}/messages` | - |
| GET | `/api/folders/{folder_id}/messages` | - |
| GET | `/api/messages/{message_id}` | - |

## Технологии

Python, FastAPI, Pydantic, PyJWT, Passlib, Uvicorn

## Запуск

```bash
pip install -r requirements.txt
cd src
python3 -m uvicorn main:app --reload
```

Swagger: http://localhost:8000/docs

## Docker

```bash
docker-compose up --build
```

## Примеры

Регистрация:
```bash
curl -X POST "http://localhost:8000/api/auth/register" -H "Content-Type: application/json" -d '{"login": "user1", "firstName": "John", "lastName": "Doe", "password": "pass123"}'
```

Логин:
```bash
curl -X POST "http://localhost:8000/api/auth/login" -H "Content-Type: application/json" -d '{"login": "user1", "password": "pass123"}'
```

Создание папки (нужен токен):
```bash
curl -X POST "http://localhost:8000/api/folders" -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -d '{"name": "Inbox", "userId": 1}'
```

Создание письма:
```bash
curl -X POST "http://localhost:8000/api/folders/1/messages" -H "Content-Type: application/json" -d '{"subject": "Hi", "body": "Hello", "sender": "a@b.com", "recipient": "c@d.com"}'
```

## Тесты

```bash
pip install pytest httpx
python3 -m pytest tests/test_api.py -v
```

## Автор

Ситдиков Ришат М8О-102СВ-25
