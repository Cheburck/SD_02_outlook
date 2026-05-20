# Event Catalog

Каталог событий домена "Электронная почта"

---

## 1. UserCreated

**Описание:** Событие публикуется при успешной регистрации нового пользователя в системе.

### Metadata

| Поле | Значение |
|------|----------|
| **Event Type** | `UserCreated` |
| **Routing Key** | `user.created` |
| **Exchange** | `email_events` (topic) |
| **Producer** | Email API (Auth Service) |
| **Consumers** | Notification Service, Analytics Service, Audit Service |
| **Гарантии доставки** | At-least-once |
| **Версия** | 1.0.0 |

### Payload Schema

```json
{
  "event_id": "string (UUID)",
  "event_type": "UserCreated",
  "timestamp": "string (ISO 8601)",
  "aggregate_id": "string (user-{id})",
  "payload": {
    "id": "integer",
    "login": "string (email)",
    "firstName": "string",
    "lastName": "string",
    "createdAt": "string (ISO 8601)"
  },
  "metadata": {
    "service": "email-api",
    "version": "1.0.0"
  }
}
```

### Пример сообщения

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

### Обработчики (Consumers)

| Сервис | Действие |
|--------|----------|
| **Notification Service** | Отправка приветственного email пользователю |
| **Analytics Service** | Инкремент метрики `registrations_total` |
| **Audit Service** | Запись в лог аудита: "User {id} registered at {timestamp}" |

---

## 2. FolderCreated

**Описание:** Событие публикуется при создании новой почтовой папки пользователем.

### Metadata

| Поле | Значение |
|------|----------|
| **Event Type** | `FolderCreated` |
| **Routing Key** | `folder.created` |
| **Exchange** | `email_events` (topic) |
| **Producer** | Email API (Folders Service) |
| **Consumers** | Analytics Service, Audit Service, Search Service |
| **Гарантии доставки** | At-least-once |
| **Версия** | 1.0.0 |

### Payload Schema

```json
{
  "event_id": "string (UUID)",
  "event_type": "FolderCreated",
  "timestamp": "string (ISO 8601)",
  "aggregate_id": "string (folder-{id})",
  "payload": {
    "id": "integer",
    "name": "string",
    "userId": "integer",
    "createdAt": "string (ISO 8601)"
  },
  "metadata": {
    "service": "email-api",
    "version": "1.0.0"
  }
}
```

### Пример сообщения

```json
{
  "event_id": "660e8400-e29b-41d4-a716-446655440001",
  "event_type": "FolderCreated",
  "timestamp": "2024-01-15T11:00:00Z",
  "aggregate_id": "folder-456",
  "payload": {
    "id": 456,
    "name": "Inbox",
    "userId": 123,
    "createdAt": "2024-01-15T11:00:00Z"
  },
  "metadata": {
    "service": "email-api",
    "version": "1.0.0"
  }
}
```

### Обработчики (Consumers)

| Сервис | Действие |
|--------|----------|
| **Analytics Service** | Инкремент метрики `folders_created_total` |
| **Audit Service** | Запись в лог аудита: "Folder {id} created by user {userId}" |
| **Search Service** | Индексация папки для поиска |

---

## 3. MessageCreated

**Описание:** Событие публикуется при создании нового письма в почтовой папке.

### Metadata

| Поле | Значение |
|------|----------|
| **Event Type** | `MessageCreated` |
| **Routing Key** | `message.created` |
| **Exchange** | `email_events` (topic) |
| **Producer** | Email API (Messages Service) |
| **Consumers** | Notification Service, Analytics Service, Audit Service, Search Service |
| **Гарантии доставки** | At-least-once |
| **Версия** | 1.0.0 |

### Payload Schema

```json
{
  "event_id": "string (UUID)",
  "event_type": "MessageCreated",
  "timestamp": "string (ISO 8601)",
  "aggregate_id": "string (message-{id})",
  "payload": {
    "id": "integer",
    "subject": "string",
    "sender": "string (email)",
    "recipient": "string (email)",
    "folderId": "integer",
    "createdAt": "string (ISO 8601)"
  },
  "metadata": {
    "service": "email-api",
    "version": "1.0.0"
  }
}
```

### Пример сообщения

```json
{
  "event_id": "770e8400-e29b-41d4-a716-446655440002",
  "event_type": "MessageCreated",
  "timestamp": "2024-01-15T12:00:00Z",
  "aggregate_id": "message-789",
  "payload": {
    "id": 789,
    "subject": "Meeting Tomorrow",
    "sender": "alice@example.com",
    "recipient": "bob@example.com",
    "folderId": 456,
    "createdAt": "2024-01-15T12:00:00Z"
  },
  "metadata": {
    "service": "email-api",
    "version": "1.0.0"
  }
}
```

### Обработчики (Consumers)

| Сервис | Действие |
|--------|----------|
| **Notification Service** | Отправка push/email уведомления получателю |
| **Analytics Service** | Инкремент метрик `messages_sent_total`, `messages_by_user` |
| **Audit Service** | Запись в лог аудита: "Message {id} sent from {sender} to {recipient}" |
| **Search Service** | Индексация письма для полнотекстового поиска |

---

## Сводная таблица событий

| Событие | Routing Key | Producer | Consumers |
|---------|-------------|----------|-----------|
| UserCreated | `user.created` | Auth Service | Notification, Analytics, Audit |
| FolderCreated | `folder.created` | Folders Service | Analytics, Audit, Search |
| MessageCreated | `message.created` | Messages Service | Notification, Analytics, Audit, Search |

---

## Топология RabbitMQ

```
                    ┌─────────────────────────┐
                    │   email_events (topic)  │
                    │       Exchange          │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
  user.created           folder.created          message.created
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ notifications│        │  analytics   │        │    audit     │
│    queue     │        │    queue     │        │    queue     │
│ (user.created)│        │     (#)      │        │     (#)      │
│ (message.    │        │              │        │              │
│  created)    │        │              │        │              │
└──────────────┘        └──────────────┘        └──────────────┘
```

---

## Обработка ошибок

### Идемпотентность

Все потребители должны обрабатывать дублирующиеся сообщения:
- Проверка `event_id` в хранилище обработанных событий
- Пропуск уже обработанных событий

### Retry Policy

При ошибке обработки:
1. Логирование ошибки
2. NACK с `requeue=true`
3. Максимум 3 попыток
4. Dead Letter Queue после исчерпания попыток

### Dead Letter Queue

Для каждой очереди настраивается DLQ:
- `notifications_queue.dlq`
- `analytics_queue.dlq`
- `audit_queue.dlq`

Сообщения перемещаются в DLQ после 3 неудачных попыток обработки.
