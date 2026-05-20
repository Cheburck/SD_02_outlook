-- Schema for Email System (Outlook)
-- Database: PostgreSQL
-- Author: Sitdikov Risat M8O-102SV-25

-- Enable UUID extension (optional, using SERIAL for simplicity)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABLE: users
-- Описание: Пользователи системы электронной почты
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ограничения
    CONSTRAINT chk_users_login_not_empty CHECK (length(trim(login)) > 0),
    CONSTRAINT chk_users_first_name_not_empty CHECK (length(trim(first_name)) > 0),
    CONSTRAINT chk_users_last_name_not_empty CHECK (length(trim(last_name)) > 0)
);

-- ============================================
-- TABLE: folders
-- Описание: Почтовые папки пользователей
-- ============================================
CREATE TABLE IF NOT EXISTS folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Внешний ключ
    CONSTRAINT fk_folders_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- Ограничения
    CONSTRAINT chk_folders_name_not_empty CHECK (length(trim(name)) > 0)
);

-- ============================================
-- TABLE: messages
-- Описание: Электронные письма в папках
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    folder_id INTEGER NOT NULL,
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    sender VARCHAR(255) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Внешний ключ
    CONSTRAINT fk_messages_folder
        FOREIGN KEY (folder_id)
        REFERENCES folders(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- Ограничения
    CONSTRAINT chk_messages_subject_not_empty CHECK (length(trim(subject)) > 0),
    CONSTRAINT chk_messages_body_not_empty CHECK (length(trim(body)) > 0),
    CONSTRAINT chk_messages_sender_not_empty CHECK (length(trim(sender)) > 0),
    CONSTRAINT chk_messages_recipient_not_empty CHECK (length(trim(recipient)) > 0)
);

-- ============================================
-- INDEXES
-- ============================================

-- Индекс для поиска пользователя по логину (GET /api/users/login/{login})
-- Уникальный индекс уже создан автоматически для UNIQUE колонки login
-- Дополнительный индекс не требуется

-- Индекс для поиска пользователей по имени и фамилии (GET /api/users/search)
-- Составной индекс для оптимизации поиска по маске
CREATE INDEX IF NOT EXISTS idx_users_first_name ON users(first_name);
CREATE INDEX IF NOT EXISTS idx_users_last_name ON users(last_name);
CREATE INDEX IF NOT EXISTS idx_users_name_combined ON users(last_name, first_name);

-- Индекс для связи folders с users (фильтрация по владельцу)
CREATE INDEX IF NOT EXISTS idx_folders_user_id ON folders(user_id);

-- Индекс для получения писем в папке (GET /api/folders/{id}/messages)
CREATE INDEX IF NOT EXISTS idx_messages_folder_id ON messages(folder_id);

-- Индекс для поиска писем по отправителю/получателю (потенциальные будущие запросы)
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender);
CREATE INDEX IF NOT EXISTS idx_messages_recipient ON messages(recipient);

-- Индекс для сортировки по дате создания
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_folders_created_at ON folders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON TABLE users IS 'Пользователи системы электронной почты';
COMMENT ON COLUMN users.id IS 'Первичный ключ, автоинкремент';
COMMENT ON COLUMN users.login IS 'Уникальный логин пользователя';
COMMENT ON COLUMN users.password_hash IS 'Хэш пароля (SHA256)';
COMMENT ON COLUMN users.first_name IS 'Имя пользователя';
COMMENT ON COLUMN users.last_name IS 'Фамилия пользователя';
COMMENT ON COLUMN users.created_at IS 'Дата и время создания записи';

COMMENT ON TABLE folders IS 'Почтовые папки пользователей';
COMMENT ON COLUMN folders.id IS 'Первичный ключ, автоинкремент';
COMMENT ON COLUMN folders.name IS 'Название папки (Inbox, Sent, Drafts, etc.)';
COMMENT ON COLUMN folders.user_id IS 'Внешний ключ на таблицу users (владелец папки)';
COMMENT ON COLUMN folders.created_at IS 'Дата и время создания папки';

COMMENT ON TABLE messages IS 'Электронные письма';
COMMENT ON COLUMN messages.id IS 'Первичный ключ, автоинкремент';
COMMENT ON COLUMN messages.folder_id IS 'Внешний ключ на таблицу folders (папка назначения)';
COMMENT ON COLUMN messages.subject IS 'Тема письма';
COMMENT ON COLUMN messages.body IS 'Тело письма';
COMMENT ON COLUMN messages.sender IS 'Email отправителя';
COMMENT ON COLUMN messages.recipient IS 'Email получателя';
COMMENT ON COLUMN messages.created_at IS 'Дата и время создания письма';

COMMENT ON INDEX idx_users_first_name IS 'Индекс для поиска по имени';
COMMENT ON INDEX idx_users_last_name IS 'Индекс для поиска по фамилии';
COMMENT ON INDEX idx_users_name_combined IS 'Составной индекс для поиска по имени и фамилии';
COMMENT ON INDEX idx_folders_user_id IS 'Индекс для связи папок с пользователями';
COMMENT ON INDEX idx_messages_folder_id IS 'Индекс для получения писем в папке';
COMMENT ON INDEX idx_messages_sender IS 'Индекс для поиска писем по отправителю';
COMMENT ON INDEX idx_messages_recipient IS 'Индекс для поиска писем по получателю';
COMMENT ON INDEX idx_messages_created_at IS 'Индекс для сортировки писем по дате';
