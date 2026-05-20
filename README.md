# Email REST API (Outlook)

REST API для управления почтой с базой данных PostgreSQL. Курс "Архитектура программных систем".

## Домашнее задание №3

Проектирование и оптимизация реляционной базы данных для системы электронной почты.


## Сущности

- **User** - пользователь системы
- **Folder** - почтовая папка пользователя
- **Message** - электронное письмо

## Схема базы данных

### Таблица: users

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| id | SERIAL | PRIMARY KEY | Первичный ключ |
| login | VARCHAR(255) | NOT NULL UNIQUE | Уникальный логин |
| password_hash | VARCHAR(255) | NOT NULL | Хэш пароля |
| first_name | VARCHAR(100) | NOT NULL | Имя |
| last_name | VARCHAR(100) | NOT NULL | Фамилия |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |

### Таблица: folders

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| id | SERIAL | PRIMARY KEY | Первичный ключ |
| name | VARCHAR(255) | NOT NULL | Название папки |
| user_id | INTEGER | NOT NULL, FK → users(id) | Владелец папки |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |

### Таблица: messages

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| id | SERIAL | PRIMARY KEY | Первичный ключ |
| folder_id | INTEGER | NOT NULL, FK → folders(id) | Папка назначения |
| subject | VARCHAR(500) | NOT NULL | Тема письма |
| body | TEXT | NOT NULL | Тело письма |
| sender | VARCHAR(255) | NOT NULL | Email отправителя |
| recipient | VARCHAR(255) | NOT NULL | Email получателя |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |

### Индексы

| Индекс | Таблица | Колонки | Назначение |
|--------|---------|---------|------------|
| users_login_key | users | login | UNIQUE индекс (автоматически) |
| idx_users_first_name | users | first_name | Поиск по имени |
| idx_users_last_name | users | last_name | Поиск по фамилии |
| idx_users_name_combined | users | last_name, first_name | Комбинированный поиск |
| idx_folders_user_id | folders | user_id | Связь с пользователями |
| idx_messages_folder_id | messages | folder_id | Поиск писем в папке |
| idx_messages_sender | messages | sender | Поиск по отправителю |
| idx_messages_recipient | messages | recipient | Поиск по получателю |
| idx_messages_created_at | messages | created_at DESC | Сортировка по дате |


## Endpoints API

| Метод | Endpoint | Auth | Описание |
|-------|----------|------|----------|
| POST | `/api/auth/register` | - | Регистрация пользователя |
| POST | `/api/auth/login` | - | Аутентификация |
| POST | `/api/users` | - | Создание пользователя |
| GET | `/api/users/login/{login}` | - | Поиск по логину |
| GET | `/api/users/search?firstName=&lastName=` | - | Поиск по имени/фамилии |
| POST | `/api/folders` | + | Создание папки |
| GET | `/api/folders` | + | Все папки |
| POST | `/api/folders/{folder_id}/messages` | - | Создание письма |
| GET | `/api/folders/{folder_id}/messages` | - | Письма в папке |
| GET | `/api/messages/{message_id}` | - | Письмо по ID |

## Быстрый старт

### Вариант 1: Docker Compose (рекомендуется)

```bash
# Запуск PostgreSQL и API
docker-compose up --build

# Остановка
docker-compose down
```

API доступно на: http://localhost:8000  
PostgreSQL на: localhost:5432

### Вариант 2: Локальный запуск

#### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 2. Запуск PostgreSQL

```bash
# Через Docker
docker run -d --name outlook_db \
  -e POSTGRES_DB=outlook_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine

# Или используйте локальную установку PostgreSQL
```

#### 3. Создание базы данных

```bash
# Подключение к БД
psql -h localhost -U postgres -d outlook_db

# Создание схемы
\i db/schema.sql

# Загрузка тестовых данных
\i db/data.sql
```

#### 4. Запуск API

```bash
# Установка переменных окружения
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=outlook_db
export DB_USER=postgres
export DB_PASSWORD=postgres
export SECRET_KEY=your-secret-key

# Запуск сервера
cd src
python3 -m uvicorn main:app --reload
```

Swagger UI: http://localhost:8000/docs

---

## Примеры запросов

### Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"login": "user1", "firstName": "John", "lastName": "Doe", "password": "pass123"}'
```

### Логин

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "user1", "password": "pass123"}'
```

### Создание папки

```bash
# Получить токен
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "user1", "password": "pass123"}' | jq -r '.token')

# Создать папку
curl -X POST "http://localhost:8000/api/folders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Inbox", "userId": 1}'
```

### Создание письма

```bash
curl -X POST "http://localhost:8000/api/folders/1/messages" \
  -H "Content-Type: application/json" \
  -d '{"subject": "Hello", "body": "Test message", "sender": "a@b.com", "recipient": "c@d.com"}'
```

### Поиск пользователей

```bash
# По логину
curl "http://localhost:8000/api/users/login/john.doe"

# По имени
curl "http://localhost:8000/api/users/search?firstName=John"

# По фамилии
curl "http://localhost:8000/api/users/search?lastName=Doe"
```

## Тесты

```bash
pip install pytest httpx pytest-asyncio
python3 -m pytest tests/test_api.py -v
```

## Автор

Ситдиков Ришат М8О-102СВ-25
