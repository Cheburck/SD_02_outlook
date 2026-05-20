# Email REST API (Outlook) с MongoDB

REST API для управления почтой с использованием MongoDB. Курс "Архитектура программных систем".

## Сущности

- **Folder** - почтовая папка
- **Message** - письмо
- **User** - пользователь

## Endpoints

| Метод | Endpoint | Auth | Описание |
|-------|----------|------|----------|
| POST | `/api/auth/register` | - | Регистрация нового пользователя |
| POST | `/api/auth/login` | - | Аутентификация пользователя |
| POST | `/api/users` | - | Создание пользователя |
| GET | `/api/users/login/{login}` | - | Поиск пользователя по логину |
| GET | `/api/users/search` | - | Поиск пользователя по маске имени и фамилии |
| POST | `/api/folders` | + | Создание новой почтовой папки |
| GET | `/api/folders` | + | Получение перечня всех папок |
| POST | `/api/folders/{folder_id}/messages` | - | Создание нового письма в папке |
| GET | `/api/folders/{folder_id}/messages` | - | Получение всех писем в папке |
| GET | `/api/messages/{message_id}` | - | Получение письма по коду |

## Технологии

Python, FastAPI, Pydantic, PyJWT, Passlib, Uvicorn, MongoDB

## Запуск с Docker (рекомендуется)

### 1. Запуск контейнеров

```bash
docker-compose up --build
```

Это запустит:
- MongoDB на порту 27017
- API на порту 8000

### 2. Проверка работы

```bash
# Проверка health endpoint
curl http://localhost:8000/health

# Swagger UI
open http://localhost:8000/docs
```

### 3. Остановка

```bash
docker-compose down
```

## Локальный запуск

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск MongoDB (через Docker)

```bash
docker run -d -p 27017:27017 --name email_mongodb mongo:7
```

### 3. Запуск API

```bash
cd src
python3 -m uvicorn main:app --reload
```

### 4. Переменные окружения

```bash
export MONGODB_URI=mongodb://localhost:27017
export MONGODB_DATABASE=email_db
export SECRET_KEY=your-secret-key-change-in-production
```

## Примеры запросов

### Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "user1",
    "firstName": "John",
    "lastName": "Doe",
    "password": "pass123"
  }'
```

### Логин

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "user1",
    "password": "pass123"
  }'
```

### Создание папки (нужен токен)

```bash
TOKEN="your_jwt_token_here"

curl -X POST "http://localhost:8000/api/folders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Inbox",
    "userId": "65a1b2c3d4e5f6789abcdef0"
  }'
```

### Создание письма

```bash
curl -X POST "http://localhost:8000/api/folders/65a1b2c3d4e5f6789abcdef1/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Hello",
    "body": "This is a test message",
    "sender": "sender@example.com",
    "recipient": "recipient@example.com"
  }'
```

### Получение писем из папки

```bash
curl "http://localhost:8000/api/folders/65a1b2c3d4e5f6789abcdef1/messages"
```

### Поиск пользователя по логину

```bash
curl "http://localhost:8000/api/users/login/john.doe"
```

### Поиск пользователей по имени

```bash
curl "http://localhost:8000/api/users/search?firstName=John&lastName=Doe"
```

## MongoDB: Запросы и валидация

### Подключение к MongoDB

```bash
# Через mongosh
mongosh mongodb://localhost:27017/email_db
```

### Загрузка тестовых данных

```bash
# В mongosh
use email_db
load("/data/data.json")

# Или через mongoimport
mongoimport --db email_db --collection users --file data.json --jsonArray
```

### Выполнение скрипта валидации

```bash
# В mongosh
use email_db
load("validation.js")
```

### Примеры MongoDB запросов

См. файл `queries.js` для полных примеров CRUD операций.

```javascript
// Поиск пользователя по логину
db.users.findOne({ login: "john.doe" })

// Поиск по маске имени
db.users.find({ firstName: { $regex: "John", $options: "i" } })

// Получение всех папок пользователя
db.folders.find({ userId: ObjectId("...") })

// Получение писем из папки
db.messages.find({ folderId: ObjectId("...") }).sort({ createdAt: -1 })

// Агрегация: количество писем в каждой папке
db.folders.aggregate([
  { $lookup: {
      from: "messages",
      localField: "_id",
      foreignField: "folderId",
      as: "messages"
  }},
  { $project: {
      name: 1,
      messageCount: { $size: "$messages" }
  }}
])
```

## Проектирование базы данных

### Коллекции

1. **users** - пользователи
   - Индексы: `login` (unique), `firstName + lastName`

2. **folders** - почтовые папки
   - Индексы: `userId`

3. **messages** - письма
   - Индексы: `folderId`, `createdAt`, `sender`, `recipient`

### Embedded vs References

Все сущности хранятся в **отдельных коллекциях** с использованием **references**:

**Обоснование:**
- Независимый CRUD для каждой сущности
- Избегание дублирования данных
- Поддержка большого количества писем (лимит 16MB на документ)
- Гибкость запросов через `$lookup`
- Совместимость с REST API endpoints

См. `schema_design.md` для подробного описания.

## Тесты

```bash
pip install pytest httpx pytest-asyncio
python3 -m pytest tests/test_api.py -v
```

## Автор

Ситдиков Ришат М8О-102СВ-25
