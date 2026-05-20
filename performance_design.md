# Стратегия кеширования и Rate Limiting

## Email REST API (Outlook)

---

## 1. Анализ производительности

### Часто выполняемые операции (Hot Paths)

| Endpoint | Частота | Описание |
|----------|---------|----------|
| `GET /api/users/login/{login}` | Высокая | Аутентификация, проверка существования пользователя |
| `GET /api/folders/{folder_id}/messages` | Высокая | Чтение писем в папке (основной сценарий использования) |
| `GET /api/messages/{message_id}` | Высокая | Чтение конкретного письма |
| `GET /api/folders` | Средняя | Получение списка папок пользователя |

### Медленные операции

| Endpoint | Причина медленной работы |
|----------|-------------------------|
| `GET /api/users/search` | LIKE запросы с маской по имени/фамилии, сканирование индексов |
| `GET /api/folders/{folder_id}/messages` | Может возвращать большое количество писем |

### Требования к производительности

- **Время отклика:** < 100ms для кешируемых GET запросов
- **Пропускная способность:** 1000+ запросов/секунду на чтение
- **Доступность:** 99.9%

---

## 2. Стратегия кеширования

### Обзор

Используется паттерн **Cache-Aside (Lazy Loading)**:
1. При запросе сначала проверяется кеш
2. При попадании (cache hit) — данные возвращаются из кеша
3. При промахе (cache miss) — данные читаются из БД и записываются в кеш

### Таблица кешируемых данных

| Данные | Ключ кеша | TTL | Стратегия | Инвалидация |
|--------|-----------|-----|-----------|-------------|
| Пользователь по логину | `user:login:{login}` | 300 сек | Cache-Aside | При изменении профиля |
| Пользователь по ID | `user:id:{id}` | 300 сек | Cache-Aside | При изменении профиля |
| Письмо по ID | `message:{id}` | 120 сек | Cache-Aside | При удалении письма |
| Письма в папке | `folder:{id}:messages` | 60 сек | Cache-Aside | При создании письма в папке |
| Папки пользователя | `user:{id}:folders` | 300 сек | Cache-Aside | При создании/удалении папки |

### Почему выбраны эти TTL

- **Пользователи (5 мин):** Данные редко меняются, но логин/пароль могут обновляться
- **Письма (1-2 мин):** Высокая частота изменений, но чтение происходит часто
- **Папки (5 мин):** Структура папок стабильна, изменения редки

### Инвалидация кеша

```python
# При создании письма
cache.delete(f"folder:{folder_id}:messages")

# При удалении письма
cache.delete(f"message:{message_id}")

# При создании папки
cache.delete(f"user:{user_id}:folders")
```

---

## 3. Rate Limiting

### Алгоритмы

| Endpoint | Алгоритм | Лимит | Окно | Обоснование |
|----------|----------|-------|------|-------------|
| `POST /api/auth/login` | Token Bucket | 10 запросов | 1 минута | Защита от перебора паролей |
| `POST /api/auth/register` | Fixed Window | 5 запросов | 1 минута | Защита от массовых регистраций |
| `POST /api/users` | Fixed Window | 10 запросов | 1 минута | Ограничение создания пользователей |
| `GET /api/users/search` | Sliding Window | 30 запросов | 1 минута | Защита от злоупотребления поиском |
| Остальные GET | Sliding Window | 100 запросов | 1 минута | Стандартные лимиты |
| Остальные POST | Sliding Window | 50 запросов | 1 минута | Ограничение записи |

### Почему выбраны эти алгоритмы

- **Token Bucket для login:** Позволяет кратковременные всплески (пользователь может несколько раз ошибиться при вводе пароля), но ограничивает среднюю частоту
- **Fixed Window для register:** Простая реализация, достаточно для защиты от спама
- **Sliding Window для GET:** Более точный учёт, плавное ограничение без резких скачков на границах окон

### HTTP заголовки

Все endpoints с rate limiting возвращают заголовки:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1700000060
```

При превышении лимита:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 45
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1700000060
```

---

## 4. Реализация

### Технологии

- **Redis:** Хранение кеша и счётчиков rate limiting
- **fastapi-cache2:** Декораторы для кеширования
- **slowapi:** Rate limiting middleware для FastAPI

### Структура ключей Redis

```
# Кеш
user:login:{login}
user:id:{id}
message:{id}
folder:{id}:messages
user:{id}:folders

# Rate limiting
ratelimit:{endpoint}:{identifier}:{window}
```

### Метрики для мониторинга

| Метрика | Описание | Как измерить |
|---------|----------|--------------|
| Cache Hit Rate | % запросов, обслуженных из кеша | `hits / (hits + misses) * 100` |
| Average Response Time | Среднее время ответа | Логирование времени выполнения |
| Rate Limit Rejections | Количество 429 ответов | Счётчик отклонённых запросов |
| Redis Memory Usage | Использование памяти Redis | `INFO memory` в Redis |

### Формула Cache Hit Rate

```
Cache Hit Rate = (Cache Hits) / (Cache Hits + Cache Misses) * 100%

Целевое значение: > 80% для GET endpoints
```

---

## 5. Ожидаемый эффект

### До оптимизации

| Endpoint | Среднее время | P95 |
|----------|--------------|-----|
| GET /api/users/login/{login} | 15ms | 25ms |
| GET /api/folders/{id}/messages | 50ms | 150ms |
| GET /api/messages/{id} | 10ms | 20ms |
| GET /api/users/search | 100ms | 300ms |

### После кеширования (ожидаемое)

| Endpoint | Среднее время | P95 | Улучшение |
|----------|--------------|-----|-----------|
| GET /api/users/login/{login} | 2ms | 5ms | 7.5x |
| GET /api/folders/{id}/messages | 5ms | 10ms | 10x |
| GET /api/messages/{id} | 2ms | 5ms | 5x |
| GET /api/users/search | 80ms | 200ms | 1.25x |

### Эффект от Rate Limiting

- Защита от DDoS атак на уровне приложения
- Предотвращение исчерпания ресурсов БД

---

## 6. Конфигурация

### Переменные окружения

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Rate Limiting
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_REGISTER=5/minute
RATE_LIMIT_SEARCH=30/minute

# Кеширование
CACHE_TTL_USER=300
CACHE_TTL_MESSAGE=120
CACHE_TTL_FOLDER_MESSAGES=60
```

---

**Автор:** Ситдиков Ришат М8О-102СВ-25
