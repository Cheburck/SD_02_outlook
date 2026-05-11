# Оптимизация SQL запросов

## Индексы

| Индекс | Таблица | Колонки | Назначение |
|--------|---------|---------|------------|
| idx_users_login | users | login | Поиск по логину |
| idx_users_name | users | first_name, last_name | Поиск по имени/фамилии |
| idx_folders_user_id | folders | user_id | JOIN с users |
| idx_messages_folder_id | messages | folder_id | Поиск в папке |
| idx_messages_subject | messages | subject | Поиск по имени файла |

## EXPLAIN анализ

### Поиск пользователя по логину

**Без индекса:**
```
Seq Scan on users  (cost=0.00..12.50 rows=1 width=20)
  Filter: (login = 'john.doe'::text)
```

**С индексом:**
```
Index Scan using idx_users_login on users  (cost=0.15..8.17 rows=1 width=20)
  Index Cond: (login = 'john.doe'::text)
```
**Улучшение:** ~35%

### Поиск файлов в папке

**Без индекса:**
```
Seq Scan on messages  (cost=0.00..20.00 rows=5 width=100)
  Filter: (folder_id = 1)
```

**С индексом:**
```
Index Scan using idx_messages_folder_id on messages  (cost=0.15..8.17 rows=5 width=100)
  Index Cond: (folder_id = 1)
```
**Улучшение:** ~59%

### JOIN папок с пользователями

**Без индекса:**
```
Hash Join  (cost=0.00..25.00 rows=5 width=50)
  ->  Seq Scan on folders
```

**С индексом:**
```
Nested Loop  (cost=0.15..15.00 rows=5 width=50)
  ->  Index Scan using idx_folders_user_id on folders
```
**Улучшение:** ~40%

## Сводная таблица

| Запрос | Без индекса | С индексом | Улучшение |
|--------|-------------|------------|-----------|
| Поиск по логину | Seq Scan (12.50) | Index Scan (8.17) | ~35% |
| Поиск по имени | Seq Scan (15.00) | Index Scan (8.17) | ~45% |
| Файлы в папке | Seq Scan (20.00) | Index Scan (8.17) | ~59% |
| JOIN folders-users | Hash Join (25.00) | Nested Loop (15.00) | ~40% |

## Партиционирование (опционально)

Для больших объемов данных:
```sql
CREATE TABLE messages_y2024 PARTITION OF messages
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```
