# Email REST API (Outlook)

REST API для управления почтой с базой данных PostgreSQL и Redis кешированием. Курс "Архитектура программных систем".

## Домашние задания

- **ДЗ №3**: Проектирование и оптимизация реляционной базы данных
- **ДЗ №5**: Оптимизация производительности через кеширование и rate limiting
- **ДЗ №6**: Проектирование Event-Driven архитектуры

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

**Почему выбраны эти индексы:**
- `login` — UNIQUE для быстрой проверки при аутентификации
- `first_name`, `last_name` — для поиска пользователей по маске имени
- `user_id` в folders — для быстрого получения папок пользователя
- `folder_id` в messages — для получения всех писем в папке
- `sender`, `recipient` — для поиска писем по отправителю/получателю
- `created_at DESC` — для сортировки писем по дате (новые сверху)

## Endpoints API

| Метод | Endpoint | Rate Limit | Кеш | Описание |
|-------|----------|------------|-----|----------|
| POST | `/api/auth/register` | 5/мин | ❌ | Регистрация пользователя |
| POST | `/api/auth/login` | 10/мин | ✅ | Аутентификация |
| POST | `/api/users` | 10/мин | ❌ | Создание пользователя |
| GET | `/api/users/login/{login}` | 100/мин | ✅ (5 мин) | Поиск по логину |
| GET | `/api/users/search` | 30/мин | ✅ (1 мин) | Поиск по имени/фамилии |
| POST | `/api/folders` | 20/мин | ❌ | Создание папки |
| GET | `/api/folders` | 100/мин | ✅ (1 мин) | Все папки |
| GET | `/api/users/{id}/folders` | 100/мин | ✅ (5 мин) | Папки пользователя |
| POST | `/api/messages` | 30/мин | ❌ | Создание письма |
| GET | `/api/folders/{id}/messages` | 100/мин | ✅ (1 мин) | Письма в папке |
| GET | `/api/messages/{id}` | 100/мин | ✅ (2 мин) | Письмо по ID |

## Быстрый старт

### Docker Compose (рекомендуется)

```bash
# Запуск PostgreSQL, Redis и API
docker-compose up --build

# Остановка
docker-compose down
```

API доступно на: http://localhost:8000  
PostgreSQL на: localhost:5432  
Redis на: localhost:6379

### Локальный запуск

#### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 2. Запуск PostgreSQL и Redis

```bash
# PostgreSQL
docker run -d --name outlook_db \
  -e POSTGRES_DB=outlook_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine

# Redis
docker run -d --name outlook_redis \
  -p 6379:6379 \
  redis:7-alpine
```

#### 3. Создание базы данных

```bash
psql -h localhost -U postgres -d outlook_db -f db/schema.sql
psql -h localhost -U postgres -d outlook_db -f db/data.sql
```

#### 4. Запуск API

```bash
export DB_HOST=localhost
export DB_NAME=outlook_db
export DB_USER=postgres
export DB_PASSWORD=postgres
export REDIS_HOST=localhost
export REDIS_PORT=6379
export SECRET_KEY=your-secret-key

cd src
python3 -m uvicorn main:app --reload
```

Swagger UI: http://localhost:8000/docs

---

## Стратегия кеширования

Используется паттерн **Cache-Aside (Lazy Loading)**:

1. При запросе сначала проверяется Redis кеш
2. При попадании — данные возвращаются из кеша
3. При промахе — данные читаются из БД и записываются в кеш

### Кешируемые данные

| Данные | Ключ кеша | TTL |
|--------|-----------|-----|
| Пользователь по логину | `user:login:{login}` | 5 мин |
| Письмо по ID | `message:{id}` | 2 мин |
| Письма в папке | `folder:{id}:messages` | 1 мин |
| Папки пользователя | `user:{id}:folders` | 5 мин |

### Инвалидация кеша

При создании/обновлении данных соответствующие ключи кеша удаляются:
- Создание письма → инвалидация `folder:{id}:messages`
- Создание папки → инвалидация `user:{id}:folders`
- Создание пользователя → инвалидация `user:{id}:folders`

## Rate Limiting

Используется **slowapi** с Redis бэкендом.

### Лимиты

| Endpoint | Лимит | Алгоритм | Обоснование |
|----------|-------|----------|-------------|
| POST /api/auth/login | 10/мин | Token Bucket | Защита от брутфорса |
| POST /api/auth/register | 5/мин | Fixed Window | Защита от спама |
| GET /api/users/search | 30/мин | Sliding Window | Защита от злоупотребления поиском |
| Остальные GET | 100/мин | Sliding Window | Стандартные лимиты |
| Остальные POST | 50/мин | Sliding Window | Ограничение записи |

### Заголовки

Все ответы содержат заголовки:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1700000060
```

При превышении лимита возвращается **429 Too Many Requests** с заголовком `Retry-After`.

---

## Примеры запросов

### Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"login": "user1", "password": "pass123"}'
```

### Логин

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "user1", "password": "pass123"}'
```

### Поиск пользователей

```bash
# По логину
curl "http://localhost:8000/api/users/login/user1"

# По имени
curl "http://localhost:8000/api/users/search?firstName=John"
```

### Создание папки

```bash
curl -X POST "http://localhost:8000/api/folders" \
  -H "Content-Type: application/json" \
  -d '{"name": "Inbox", "userId": 1}'
```

### Создание письма

```bash
curl -X POST "http://localhost:8000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{"subject": "Hello", "body": "Test message", "sender": "a@b.com", "recipient": "c@d.com", "folderId": 1}'
```

## Тесты

```bash
pip install pytest httpx pytest-asyncio
python3 -m pytest tests/test_api.py -v
```

## Автор

Ситдиков Ришат М8О-102СВ-25

---

## Event-Driven архитектура (ДЗ №6)

### События системы

| Событие | Описание | Routing Key |
|---------|----------|-------------|
| `UserCreated` | Новый пользователь зарегистрировался | `user.created` |
| `FolderCreated` | Пользователь создал почтовую папку | `folder.created` |
| `MessageCreated` | Новое письмо создано в папке | `message.created` |

### Топология RabbitMQ

**Exchange:** `email_events` (topic)

**Queues:**
- `notifications_queue` — уведомления (user.created, message.created)
- `analytics_queue` — аналитика (все события)
- `audit_queue` — аудит (все события)

### Запуск с RabbitMQ

```bash
# Запуск всех сервисов (PostgreSQL, Redis, RabbitMQ, API)
docker-compose up --build

# Management UI RabbitMQ
# http://localhost:15672 (guest/guest)
```

### Потребители событий

Пример запуска consumer для аналитики:

```bash
cd src
python3 -c "from events.consumer import create_analytics_consumer; create_analytics_consumer().start_consuming()"
```

### CQRS

**Write Model (команды):**
- POST /api/auth/register → CreateUser
- POST /api/folders → CreateFolder
- POST /api/messages → CreateMessage

**Read Model (запросы):**
- GET /api/users/* → чтение из БД/кеша
- GET /api/folders/* → чтение из БД/кеша
- GET /api/messages/* → чтение из БД/кеша

События публикуются после успешной записи и используются для:
- Уведомлений (отправка email)
- Аналитики (сбор метрик)
- Аудита (логирование действий)
- Поиска (индексация)

См. подробнее в [event_driven_design.md](event_driven_design.md) и [event_catalog.md](event_catalog.md).
