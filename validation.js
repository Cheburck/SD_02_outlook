// MongoDB Schema Validation для Email API
// Скрипт создаёт валидацию схем для коллекций базы данных

// ============================================================================
// ПОДГОТОВКА
// ============================================================================
use email_db;

// ============================================================================
// 1. ВАЛИДАЦИЯ ДЛЯ КОЛЛЕКЦИИ users
// ============================================================================

// Удаляем коллекцию если существует (для пересоздания с валидацией)
db.users.drop();

// Создаём коллекцию с валидацией
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["login", "firstName", "lastName", "password_hash"],
      additionalProperties: false,
      properties: {
        login: {
          bsonType: "string",
          description: "Логин пользователя должен быть строкой",
          minLength: 3,
          maxLength: 50,
          pattern: "^[a-zA-Z0-9_.-]+$"
        },
        firstName: {
          bsonType: "string",
          description: "Имя должно быть строкой",
          minLength: 1,
          maxLength: 100,
          pattern: "^[a-zA-Zа-яА-ЯёЁ\\s-]+$"
        },
        lastName: {
          bsonType: "string",
          description: "Фамилия должна быть строкой",
          minLength: 1,
          maxLength: 100,
          pattern: "^[a-zA-Zа-яА-ЯёЁ\\s-]+$"
        },
        password_hash: {
          bsonType: "string",
          description: "Хэш пароля должен быть строкой минимум 10 символов",
          minLength: 10
        },
        createdAt: {
          bsonType: "date",
          description: "Дата создания должна быть типом Date"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

// Создаём индексы
db.users.createIndex({ login: 1 }, { unique: true });
db.users.createIndex({ firstName: 1, lastName: 1 });

// ============================================================================
// 2. ВАЛИДАЦИЯ ДЛЯ КОЛЛЕКЦИИ folders
// ============================================================================

db.folders.drop();

db.createCollection("folders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "userId"],
      additionalProperties: false,
      properties: {
        name: {
          bsonType: "string",
          description: "Имя папки должно быть строкой",
          minLength: 1,
          maxLength: 100,
          pattern: "^[a-zA-Z0-9а-яА-ЯёЁ\\s_-]+$"
        },
        userId: {
          bsonType: "objectId",
          description: "userId должен быть ObjectId"
        },
        createdAt: {
          bsonType: "date",
          description: "Дата создания должна быть типом Date"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

// Создаём индексы
db.folders.createIndex({ userId: 1 });

// ============================================================================
// 3. ВАЛИДАЦИЯ ДЛЯ КОЛЛЕКЦИИ messages
// ============================================================================

db.messages.drop();

db.createCollection("messages", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["folderId", "subject", "body", "sender", "recipient"],
      additionalProperties: false,
      properties: {
        folderId: {
          bsonType: "objectId",
          description: "folderId должен быть ObjectId"
        },
        subject: {
          bsonType: "string",
          description: "Тема письма должна быть строкой",
          minLength: 1,
          maxLength: 200
        },
        body: {
          bsonType: "string",
          description: "Тело письма должно быть строкой",
          minLength: 1,
          maxLength: 10000
        },
        sender: {
          bsonType: "string",
          description: "Отправитель должен быть email строкой",
          minLength: 5,
          maxLength: 100,
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        recipient: {
          bsonType: "string",
          description: "Получатель должен быть email строкой",
          minLength: 5,
          maxLength: 100,
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        createdAt: {
          bsonType: "date",
          description: "Дата создания должна быть типом Date"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

// Создаём индексы
db.messages.createIndex({ folderId: 1 });
db.messages.createIndex({ createdAt: -1 });
db.messages.createIndex({ sender: 1 });
db.messages.createIndex({ recipient: 1 });

// ============================================================================
// 4. ТЕСТИРОВАНИЕ ВАЛИДАЦИИ
// ============================================================================

// 4.1 Успешная вставка пользователя (должна пройти)
print("\n=== Тест 4.1: Успешная вставка пользователя ===");
try {
  db.users.insertOne({
    login: "valid_user",
    firstName: "John",
    lastName: "Doe",
    password_hash: "$5$rounds=535000$valid_hash",
    createdAt: new Date()
  });
  print("✓ Успешно: Пользователь создан");
} catch (e) {
  print("✗ Ошибка: " + e.message);
}

// 4.2 Неверный тип login (должна ошибка)
print("\n=== Тест 4.2: Неверный тип login (число вместо строки) ===");
try {
  db.users.insertOne({
    login: 12345,
    firstName: "Invalid",
    lastName: "User",
    password_hash: "hash123456"
  });
  print("✗ Ошибка валидации не сработала");
} catch (e) {
  print("✓ Успешно отклонено: " + e.message);
}

// 4.3 Слишком короткий login (должна ошибка)
print("\n=== Тест 4.3: Слишком короткий login (менее 3 символов) ===");
try {
  db.users.insertOne({
    login: "ab",
    firstName: "Short",
    lastName: "Login",
    password_hash: "hash123456"
  });
  print("✗ Ошибка валидации не сработала");
} catch (e) {
  print("✓ Успешно отклонено: " + e.message);
}

// 4.4 Отсутствие обязательного поля (должна ошибка)
print("\n=== Тест 4.4: Отсутствие обязательного поля password_hash ===");
try {
  db.users.insertOne({
    login: "no_password",
    firstName: "No",
    lastName: "Password"
  });
  print("✗ Ошибка валидации не сработала");
} catch (e) {
  print("✓ Успешно отклонено: " + e.message);
}

// 4.5 Неверный формат email в sender (должна ошибка)
print("\n=== Тест 4.5: Неверный формат email в sender ===");
try {
  db.messages.insertOne({
    folderId: ObjectId("507f1f77bcf86cd799439011"),
    subject: "Test",
    body: "Test body",
    sender: "invalid-email",
    recipient: "valid@email.com"
  });
  print("✗ Ошибка валидации не сработала");
} catch (e) {
  print("✓ Успешно отклонено: " + e.message);
}

// 4.6 Успешная вставка сообщения (должна пройти)
print("\n=== Тест 4.6: Успешная вставка сообщения ===");
try {
  // Сначала создаём папку
  var folderResult = db.folders.insertOne({
    name: "Test Folder",
    userId: ObjectId("507f1f77bcf86cd799439011"),
    createdAt: new Date()
  });
  
  db.messages.insertOne({
    folderId: folderResult.insertedId,
    subject: "Valid Subject",
    body: "Valid message body",
    sender: "sender@example.com",
    recipient: "recipient@example.com",
    createdAt: new Date()
  });
  print("✓ Успешно: Сообщение создано");
} catch (e) {
  print("✗ Ошибка: " + e.message);
}

// 4.7 Пустая тема письма (должна ошибка)
print("\n=== Тест 4.7: Пустая тема письма ===");
try {
  db.messages.insertOne({
    folderId: ObjectId("507f1f77bcf86cd799439011"),
    subject: "",
    body: "Body text",
    sender: "test@email.com",
    recipient: "test2@email.com"
  });
  print("✗ Ошибка валидации не сработала");
} catch (e) {
  print("✓ Успешно отклонено: " + e.message);
}

// 4.8 Дополнительное поле (должна ошибка при additionalProperties: false)
print("\n=== Тест 4.8: Дополнительное поле (additionalProperties) ===");
try {
  db.users.insertOne({
    login: "extra_field",
    firstName: "Extra",
    lastName: "Field",
    password_hash: "hash123456",
    unknownField: "should fail"
  });
  print("✗ Ошибка валидации не сработала");
} catch (e) {
  print("✓ Успешно отклонено: " + e.message);
}

// ============================================================================
// 5. ПРОВЕРКА СОЗДАННЫХ КОЛЛЕКЦИЙ
// ============================================================================

print("\n=== Информация о коллекциях ===");
print("Коллекция users:");
printjson(db.users.getValidationOptions());

print("\nКоллекция folders:");
printjson(db.folders.getValidationOptions());

print("\nКоллекция messages:");
printjson(db.messages.getValidationOptions());

// ============================================================================
// 6. ИЗМЕНЕНИЕ ВАЛИДАЦИИ (пример)
// ============================================================================

// Пример изменения валидации для существующей коллекции
// db.runCommand({
//   collMod: "users",
//   validator: {
//     $jsonSchema: {
//       bsonType: "object",
//       required: ["login", "firstName", "lastName", "password_hash"],
//       properties: {
//         login: {
//           bsonType: "string",
//           minLength: 5  // Изменили минимальную длину с 3 до 5
//         }
//       }
//     }
//   },
//   validationLevel: "strict"
// });

// ============================================================================
// 7. ОТКЛЮЧЕНИЕ ВАЛИДАЦИИ (для миграций)
// ============================================================================

// Временное отключение валидации для массовой вставки данных
// db.runCommand({
//   collMod: "users",
//   validationLevel: "off"
// });

// После вставки данных включить обратно
// db.runCommand({
//   collMod: "users",
//   validationLevel: "strict"
// });

print("\n=== Скрипт валидации завершён ===");
