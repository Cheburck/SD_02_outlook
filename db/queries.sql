-- Queries for Email System (Outlook) API
-- SQL запросы для всех операций API
-- Author: Sitdikov Risat M8O-102SV-25

-- ============================================
-- 1. Создание нового пользователя
-- POST /api/auth/register
-- ============================================
-- Запрос:
INSERT INTO users (login, password_hash, first_name, last_name)
VALUES ('new.user', '$5$rounds=535000$xyz789$hashed_password', 'New', 'User')
RETURNING id, login, first_name, last_name;

-- Проверка существования пользователя (перед вставкой):
SELECT id FROM users WHERE login = 'new.user';

-- ============================================
-- 2. Поиск пользователя по логину
-- GET /api/users/login/{login}
-- ============================================
-- Запрос:
SELECT id, login, first_name, last_name
FROM users
WHERE login = 'john.doe';

-- ============================================
-- 3. Поиск пользователя по маске имя и фамилии
-- GET /api/users/search?firstName={name}&lastName={surname}
-- ============================================
-- Поиск по имени (с использованием LIKE для маски):
SELECT id, login, first_name, last_name
FROM users
WHERE first_name ILIKE '%John%';

-- Поиск по фамилии:
SELECT id, login, first_name, last_name
FROM users
WHERE last_name ILIKE '%Smith%';

-- Поиск по имени и фамилии одновременно:
SELECT id, login, first_name, last_name
FROM users
WHERE first_name ILIKE '%John%'
   OR last_name ILIKE '%Smith%';

-- ============================================
-- 4. Создание новой почтовой папки
-- POST /api/folders
-- ============================================
-- Запрос:
INSERT INTO folders (name, user_id)
VALUES ('Important', 1)
RETURNING id, name, user_id;

-- Проверка существования пользователя:
SELECT id FROM users WHERE id = 1;

-- ============================================
-- 5. Получение перечня всех папок
-- GET /api/folders
-- ============================================
-- Запрос:
SELECT id, name, user_id
FROM folders
ORDER BY id;

-- Получение папок конкретного пользователя:
SELECT id, name, user_id
FROM folders
WHERE user_id = 1
ORDER BY id;

-- ============================================
-- 6. Создание нового письма в папке
-- POST /api/folders/{folder_id}/messages
-- ============================================
-- Запрос:
INSERT INTO messages (folder_id, subject, body, sender, recipient)
VALUES (1, 'Test Message', 'This is a test message body', 'sender@email.com', 'recipient@email.com')
RETURNING id, folder_id, subject, body, sender, recipient, created_at;

-- Проверка существования папки:
SELECT id FROM folders WHERE id = 1;

-- ============================================
-- 7. Получение всех писем в папке
-- GET /api/folders/{folder_id}/messages
-- ============================================
-- Запрос:
SELECT id, folder_id, subject, body, sender, recipient, created_at
FROM messages
WHERE folder_id = 1
ORDER BY created_at DESC;

-- ============================================
-- 8. Получение письма по коду (id)
-- GET /api/messages/{message_id}
-- ============================================
-- Запрос:
SELECT id, folder_id, subject, body, sender, recipient, created_at
FROM messages
WHERE id = 1;

-- ============================================
-- ДОПОЛНИТЕЛЬНЫЕ ЗАПРОСЫ (для расширения функционала)
-- ============================================

-- Поиск писем по отправителю:
SELECT id, folder_id, subject, body, sender, recipient, created_at
FROM messages
WHERE sender = 'john.doe@email.com'
ORDER BY created_at DESC;

-- Поиск писем по получателю:
SELECT id, folder_id, subject, body, sender, recipient, created_at
FROM messages
WHERE recipient = 'john.doe@email.com'
ORDER BY created_at DESC;

-- Получение количества писем в каждой папке пользователя:
SELECT f.id, f.name, COUNT(m.id) as message_count
FROM folders f
LEFT JOIN messages m ON f.id = m.folder_id
WHERE f.user_id = 1
GROUP BY f.id, f.name
ORDER BY f.id;

-- Удаление письма:
DELETE FROM messages WHERE id = 1;

-- Обновление письма:
UPDATE messages
SET subject = 'Updated Subject', body = 'Updated body text'
WHERE id = 1
RETURNING id, folder_id, subject, body, sender, recipient, created_at;

-- Удаление папки (каскадно удалит письма):
DELETE FROM folders WHERE id = 1;

-- Обновление профиля пользователя:
UPDATE users
SET first_name = 'Jonathan', last_name = 'Doe'
WHERE id = 1
RETURNING id, login, first_name, last_name;

-- ============================================
-- JOIN запросы для получения полной информации
-- ============================================

-- Получение писем с информацией о папке и владельце:
SELECT 
    m.id as message_id,
    m.subject,
    m.body,
    m.sender,
    m.recipient,
    m.created_at,
    f.id as folder_id,
    f.name as folder_name,
    u.id as user_id,
    u.login as owner_login,
    u.first_name,
    u.last_name
FROM messages m
JOIN folders f ON m.folder_id = f.id
JOIN users u ON f.user_id = u.id
WHERE m.id = 1;

-- Получение всех папок с количеством писем:
SELECT 
    f.id,
    f.name,
    f.user_id,
    u.login as owner_login,
    COUNT(m.id) as message_count
FROM folders f
JOIN users u ON f.user_id = u.id
LEFT JOIN messages m ON f.id = m.folder_id
GROUP BY f.id, f.name, f.user_id, u.login
ORDER BY f.id;
