# Event-Driven Architecture Design

## 1. Анализ событий в системе

### События (Events)

| Событие | Описание | Триггер |
|---------|----------|---------|
| `UserCreated` | Новый пользователь зарегистрировался | POST /api/auth/register |
| `FolderCreated` | Пользователь создал почтовую папку | POST /api/folders |
| `MessageCreated` | Новое письмо создано в папке | POST /api/messages |

### Команды (Commands)

| Команда | Результат |
|---------|-----------|
| `CreateUser` | → `UserCreated` |
| `CreateFolder` | → `FolderCreated` |
| `CreateMessage` | → `MessageCreated` |

### Потребители событий

| Потребитель | События | Назначение |
|-------------|---------|------------|
| **Notification Service** | UserCreated, MessageCreated | Отправка приветственных писем, уведомлений о новых сообщениях |
| **Analytics Service** | Все события | Сбор статистики, метрик использования |
| **Audit Service** | Все события | Логирование действий для аудита безопасности |
| **Search Service** | FolderCreated, MessageCreated | Индексация для поиска |

---

## 2. Архитектура Event-Driven системы

### Компоненты

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Auth      │  │   Folders   │  │  Messages   │         │
│  │   Routes    │  │   Routes    │  │   Routes    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┴────────────────┘                 │
│                           │                                 │
│                  ┌────────▼────────┐                        │
│                  │ Event Publisher │                        │
│                  └────────┬────────┘                        │
└───────────────────────────┼─────────────────────────────────┘
                            │ publish(event, routing_key)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    RabbitMQ Broker                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          email_events (Topic Exchange)                │   │
│  └───────┬──────────────────┬──────────────────┬────────┘   │
│          │                  │                  │             │
│  routing: user.created      │ routing: #       │ routing: #  │
│          folder.created     │                  │             │
│          message.created    │                  │             │
│          ▼                  ▼                  ▼             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │ notifications│   │  analytics   │   │    audit     │    │
│  │    queue     │   │    queue     │   │    queue     │    │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘    │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Notification │   │  Analytics   │   │    Audit     │
│  Consumer    │   │   Consumer   │   │   Consumer   │
└──────────────┘   └──────────────┘   └──────────────┘
```

### Топология RabbitMQ

**Exchange:**
- Name: `email_events`
- Type: `topic`
- Durable: `true`

**Queues и Routing:**

| Queue | Routing Keys | Назначение |
|-------|--------------|------------|
| `notifications_queue` | `user.created`, `message.created` | Уведомления пользователей |
| `analytics_queue` | `#` (все события) | Сбор аналитики |
| `audit_queue` | `#` (все события) | Аудит безопасности |

**Routing Keys:**
- `user.created` — события регистрации пользователей
- `folder.created` — события создания папок
- `message.created` — события создания писем

---

## 3. Гарантии доставки

### At-Least-Once Delivery

**Publisher:**
- Persistent messages (`delivery_mode=2`)
- Confirm mode от брокера
- Durable exchange

**Consumer:**
- Manual acknowledgment после успешной обработки
- Requeue при ошибке обработки
- Idempotent handlers (проверка по `event_id`)

### Структура сообщения

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "UserCreated",
  "timestamp": "2024-01-15T10:30:00Z",
  "aggregate_id": "user-123",
  "payload": {
    "id": 123,
    "login": "john@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "createdAt": "2024-01-15T10:30:00Z"
  },
  "metadata": {
    "service": "email-api",
    "version": "1.0.0"
  }
}
```

---

## 4. Применение паттерна CQRS

### Разделение операций

**Write Model (Commands):**
```
POST /api/auth/register    → CreateUserCommand
POST /api/folders          → CreateFolderCommand
POST /api/messages         → CreateMessageCommand
```

**Read Model (Queries):**
```
GET  /api/users/search     → GetUserByLoginQuery
GET  /api/folders          → GetFoldersQuery
GET  /api/folders/{id}/messages → GetMessagesQuery
GET  /api/messages/{id}    → GetMessageByIdQuery
```

### Синхронизация через события

```
┌──────────────┐     Event      ┌──────────────┐
│   Write DB   │ ──────────────▶│  Read Model  │
│  (PostgreSQL)│   UserCreated  │ (Redis Cache)│
└──────────────┘                └──────────────┘
       │                              ▲
       │ FolderCreated                │
       │ MessageCreated               │
       └──────────────────────────────┘
              (инвалидация кеша)
```

**В текущей реализации:**
- **Write:** PostgreSQL (основная БД)
- **Read:** PostgreSQL + Redis Cache
- **События:** Публикуются после успешной записи, позволяют добавить асинхронных потребителей

**Преимущества CQRS:**
- Масштабирование чтения и записи независимо
- Оптимизация моделей под конкретные запросы
- Асинхронная обработка через события

---

## 5. Метрики производительности

### Для мониторинга

| Метрика | Описание |
|---------|----------|
| `events_published_total` | Количество опубликованных событий |
| `events_consumed_total` | Количество обработанных событий |
| `event_processing_latency` | Время обработки события |
| `cache_hit_rate` | Процент попаданий в кеш |
| `rate_limit_hits_total` | Количество срабатываний rate limiting |

### Ожидаемый эффект

| Оптимизация | Ожидаемое улучшение |
|-------------|---------------------|
| Кеширование read операций | 80-90% hit rate, время отклика <50ms |
| Асинхронная обработка событий | Неблокирующий ответ API |
| Rate limiting | Защита от злоупотреблений, стабильная нагрузка |

---

## 6. Запуск

```bash
# Запуск всех сервисов
docker-compose up --build

# Проверка статус
docker-compose ps

# Логи API
docker-compose logs -f api

# Логи RabbitMQ
docker-compose logs -f rabbitmq

# Management UI RabbitMQ
# http://localhost:15672 (guest/guest)
```
