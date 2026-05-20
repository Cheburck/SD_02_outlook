#!/bin/bash
# Скрипт для загрузки тестовых данных в MongoDB
# Запуск: ./load_test_data.sh

MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017}"
DATABASE="${DATABASE:-email_db}"

echo "=== Загрузка тестовых данных в MongoDB ==="
echo "MongoDB URI: $MONGODB_URI"
echo "База данных: $DATABASE"

# Проверяем наличие mongosh
if command -v mongosh &> /dev/null; then
    MONGO_CMD="mongosh"
elif command -v mongo &> /dev/null; then
    MONGO_CMD="mongo"
else
    echo "Ошибка: mongosh или mongo не найдены. Установите MongoDB shell."
    exit 1
fi

# Загружаем данные из data.json
echo "Загрузка данных из data.json..."
$MONGO_CMD "$MONGODB_URI/$DATABASE" --eval "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('data.json', 'utf8'));

if (data.users && data.users.length > 0) {
    print('Загрузка пользователей: ' + data.users.length);
    db.users.insertMany(data.users);
}

if (data.folders && data.folders.length > 0) {
    print('Загрузка папок: ' + data.folders.length);
    db.folders.insertMany(data.folders);
}

if (data.messages && data.messages.length > 0) {
    print('Загрузка писем: ' + data.messages.length);
    db.messages.insertMany(data.messages);
}

print('Готово!');
"

echo "=== Тестовые данные загружены ==="
