# Проектирование документной модели MongoDB для Email API

## Обзор системы

Система управления электронной почтой с тремя основными сущностями:
- **Пользователь (User)** - зарегистрированный пользователь системы
- **Почтовая папка (Folder)** - папка для хранения писем
- **Письмо (Message)** - электронное письмо

## Структура коллекций

### 1. Коллекция `users`

```json
{
  "_id": ObjectId,
  "login": "string (unique, required)",
  "firstName": "string (required)",
  "lastName": "string (required)",
  "password_hash": "string (required)",
  "createdAt": "Date"
}
```

**Индексы:**
- `login` - уникальный индекс для быстрого поиска по логину
- `firstName`, `lastName` - составной индекс для поиска по имени

### 2. Коллекция `folders`

```json
{
  "_id": ObjectId,
  "name": "string (required)",
  "userId": "ObjectId (ref: users, required)",
  "createdAt": "Date"
}
```

**Индексы:**
- `userId` - индекс для поиска всех папок пользователя

### 3. Коллекция `messages`

```json
{
  "_id": ObjectId,
  "folderId": "ObjectId (ref: folders, required)",
  "subject": "string (required)",
  "body": "string (required)",
  "sender": "string (required)",
  "recipient": "string (required)",
  "createdAt": "Date"
}
```

**Индексы:**
- `folderId` - индекс для поиска писем в папке
- `createdAt` - индекс для сортировки по дате

## Обоснование выбора Embedded vs References

### Решение: Все сущности в отдельных коллекциях с использованием References

### Связь User → Folders (1:N)

**Выбрано: References (отдельные коллекции)**

**Обоснование:**

1. **Независимый жизненный цикл**: Папки могут создаваться и удаляться независимо от пользователя
2. **API требования**: Endpoints требуют отдельного доступа к папкам (`GET /api/folders`, `POST /api/folders`)
3. **Избегание дублирования**: При embedded подходе данные пользователя дублировались бы в каждой папке
4. **Гибкость запросов**: Легко найти все папки пользователя через `$lookup` или простой `find({userId})`
5. **Масштабируемость**: При большом количестве папок у пользователя embedded документ стал бы слишком большим

**Альтернатива (Embedded) - почему не подходит:**
```json
// Не рекомендуется
{
  "_id": ObjectId,
  "login": "user1",
  "folders": [
    {"name": "Inbox", "messages": [...]},
    {"name": "Sent", "messages": [...]}
  ]
}
```
Проблемы:
- Ограничение MongoDB 16MB на документ
- Сложность обновления отдельных папок
- Невозможность эффективного поиска писем across folders

### Связь Folder → Messages (1:N)

**Выбрано: References (отдельные коллекции)**

**Обоснование:**

1. **Объём данных**: Письма могут содержать большой текст, вложения (метаданные)
2. **Пагинация**: API требует получения писем с пагинацией, что сложно с embedded
3. **Частота изменений**: Письма добавляются часто, не нужно загружать весь документ папки
4. **Поиск по письмам**: Endpoints требуют поиска писем по ID (`GET /api/messages/{id}`)
5. **Агрегации**: Удобство подсчёта статистики через aggregation pipeline

**Альтернатива (Embedded) - почему не подходит:**
```json
// Не рекомендуется
{
  "_id": ObjectId,
  "name": "Inbox",
  "userId": ObjectId,
  "messages": [
    {"subject": "Hi", "body": "...", "sender": "..."},
    {"subject": "Re: Hi", "body": "...", "sender": "..."}
  ]
}
```
Проблемы:
- Быстрый рост документа (лимит 16MB)
- Неэффективное обновление (при каждом новом письме переписывается весь документ)
- Сложность с пагинацией больших списков писем

### Связь User → Messages (через Folder)

**Выбрано: Косвенная ссылка через Folder**

Письма связаны с пользователем косвенно через папку:
- `Message.folderId` → `Folder._id` → `Folder.userId` → `User._id`

Это позволяет:
- Избежать дублирования `userId` в каждом письме
- Легко перемещать письма между папками одного пользователя
- Строить эффективные aggregation pipelines

## Диаграмма связей

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   users     │         │   folders   │         │   messages  │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ _id (PK)    │◄────────│ userId (FK) │         │ _id (PK)    │
│ login       │    1:N  │ _id (PK)    │◄────────│ folderId(FK)│
│ firstName   │         │ name        │    1:N  │ subject     │
│ lastName    │         │ createdAt   │         │ body        │
│ password    │         └─────────────┘         │ sender      │
│ createdAt   │                                 │ recipient   │
└─────────────┘                                 │ createdAt   │
                                                └─────────────┘
```

## Преимущества выбранной модели

1. **Нормализация**: Минимизация дублирования данных
2. **Гибкость**: Легко добавлять новые поля без миграции больших документов
3. **Производительность**: Индексы на foreign keys ускоряют JOIN-подобные запросы
4. **Масштабируемость**: Каждая коллекция может расти независимо
5. **Совместимость с API**: Структура соответствует REST endpoints

## Индексы для оптимизации

```javascript
// users
db.users.createIndex({ login: 1 }, { unique: true })
db.users.createIndex({ firstName: 1, lastName: 1 })

// folders
db.folders.createIndex({ userId: 1 })

// messages
db.messages.createIndex({ folderId: 1 })
db.messages.createIndex({ createdAt: -1 })
```
