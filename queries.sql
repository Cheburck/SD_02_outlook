-- 1. Создание пользователя
INSERT INTO users (login, first_name, last_name, password_hash)
VALUES ('new.user', 'New', 'User', '$5$rounds=535000$abc123$hashed_password_new')
RETURNING id, login, first_name, last_name, created_at;

-- 2. Поиск пользователя по логину
SELECT id, login, first_name, last_name, created_at
FROM users WHERE login = 'john.doe';

-- 3. Поиск пользователя по маске имени
SELECT id, login, first_name, last_name, created_at
FROM users
WHERE first_name ILIKE '%John%' AND last_name ILIKE '%Doe%';

-- 4. Создание папки
INSERT INTO folders (name, user_id)
VALUES ('New Folder', 1)
RETURNING id, name, user_id, created_at;

-- 5. Получение всех папок
SELECT id, name, user_id, created_at FROM folders ORDER BY id;

-- 6. Создание файла
INSERT INTO messages (folder_id, subject, body, sender, recipient)
VALUES (1, 'newfile.txt', 'File content', 'john.doe', 'jane.smith')
RETURNING id, folder_id, subject, body, sender, recipient, created_at;

-- 7. Получение файла по имени
SELECT id, folder_id, subject, body, sender, recipient, created_at
FROM messages WHERE subject = 'report.pdf';

-- 8. Удаление файла
DELETE FROM messages WHERE id = 1 RETURNING id, subject;

-- 9. Удаление папки
DELETE FROM folders WHERE id = 1 RETURNING id, name;

-- Дополнительно: файлы в папке с владельцем
SELECT m.id, m.subject, f.name AS folder_name, u.login AS owner_login
FROM messages m
JOIN folders f ON m.folder_id = f.id
JOIN users u ON f.user_id = u.id
WHERE f.id = 1;
