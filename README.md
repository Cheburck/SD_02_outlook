# Система хранения файлов

REST API для управления файлами и папками с использованием PostgreSQL.

## Схема базы данных

### Таблицы

**users** - пользователи:
- id (SERIAL PRIMARY KEY)
- login (VARCHAR UNIQUE NOT NULL)
- first_name, last_name (VARCHAR NOT NULL)
- password_hash (VARCHAR NOT NULL)
- created_at (TIMESTAMP)

**folders** - папки:
- id (SERIAL PRIMARY KEY)
- name (VARCHAR NOT NULL)
- user_id (INTEGER REFERENCES users)
- created_at (TIMESTAMP)

**messages** - файлы:
- id (SERIAL PRIMARY KEY)
- folder_id (INTEGER REFERENCES folders)
- subject, body, sender, recipient
- created_at (TIMESTAMP)

### Индексы
- idx_users_login, idx_users_name
- idx_folders_user_id
- idx_messages_folder_id, idx_messages_subject

## Запуск

```bash
docker-compose up --build
```

API: http://localhost:8000  
PostgreSQL: localhost:5432

## API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | /api/auth/register | Регистрация |
| POST | /api/auth/login | Вход |
| POST | /api/users | Создание пользователя |
| GET | /api/users/login/{login} | Поиск по логину |
| GET | /api/users/search | Поиск по имени |
| POST | /api/folders | Создание папки |
| GET | /api/folders | Список папок |
| DELETE | /api/folders/{id} | Удаление папки |
| POST | /api/folders/{id}/messages | Создание файла |
| GET | /api/folders/{id}/messages | Файлы в папке |
| GET | /api/messages/{id} | Файл по ID |
| GET | /api/messages?subject=name | Файл по имени |
| DELETE | /api/messages/{id} | Удаление файла |

## Примеры

```bash
# Регистрация
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"login":"user","firstName":"Test","lastName":"User","password":"pass"}'

# Создание папки
curl -X POST http://localhost:8000/api/folders \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Docs","userId":1}'
```

## Файлы

- `schema.sql` - схема БД
- `data.sql` - тестовые данные
- `queries.sql` - SQL запросы
- `optimization.md` - оптимизация
