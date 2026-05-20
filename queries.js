// MongoDB Queries for Email API
// Файл содержит все CRUD операции для работы с базой данных Email системы

// ============================================================================
// ПОДГОТОВКА: Использование базы данных
// ============================================================================
use email_db;

// ============================================================================
// 1. CREATE (Вставка документов)
// ============================================================================

// 1.1 Создание пользователя
db.users.insertOne({
  login: "test.user",
  firstName: "Test",
  lastName: "User",
  password_hash: "$5$rounds=535000$xyz$hashed_password",
  createdAt: new Date()
});

// 1.2 Создание нескольких пользователей
db.users.insertMany([
  {
    login: "user1",
    firstName: "First",
    lastName: "User1",
    password_hash: "hash1",
    createdAt: new Date()
  },
  {
    login: "user2",
    firstName: "Second",
    lastName: "User2",
    password_hash: "hash2",
    createdAt: new Date()
  }
]);

// 1.3 Создание папки
db.folders.insertOne({
  name: "Important",
  userId: ObjectId("507f1f77bcf86cd799439011"),
  createdAt: new Date()
});

// 1.4 Создание письма
db.messages.insertOne({
  folderId: ObjectId("507f1f77bcf86cd799439012"),
  subject: "Test Subject",
  body: "Test message body",
  sender: "sender@email.com",
  recipient: "recipient@email.com",
  createdAt: new Date()
});

// 1.5 Добавление письма с использованием $push (если бы messages были embedded)
// В нашей модели используем insertOne для отдельной коллекции

// ============================================================================
// 2. READ (Поиск документов)
// ============================================================================

// 2.1 Поиск пользователя по логину ($eq)
db.users.findOne({ login: { $eq: "john.doe" } });

// 2.2 Поиск пользователя по точному логину (упрощённо)
db.users.findOne({ login: "john.doe" });

// 2.3 Поиск пользователей по маске имени (regex)
db.users.find({
  firstName: { $regex: "John", $options: "i" }
});

// 2.4 Поиск пользователей по маске фамилии
db.users.find({
  lastName: { $regex: "Smith", $options: "i" }
});

// 2.5 Поиск по имени И фамилии ($and)
db.users.find({
  $and: [
    { firstName: { $regex: "J", $options: "i" } },
    { lastName: { $regex: "D", $options: "i" } }
  ]
});

// 2.6 Поиск пользователей с определёнными логинами ($in)
db.users.find({
  login: { $in: ["john.doe", "jane.smith", "bob.wilson"] }
});

// 2.7 Поиск пользователей кроме определённого ($ne)
db.users.find({
  login: { $ne: "admin" }
});

// 2.8 Поиск пользователей по дате регистрации ($gt, $lt)
db.users.find({
  createdAt: {
    $gt: new Date("2025-01-15T00:00:00Z"),
    $lt: new Date("2025-01-20T00:00:00Z")
  }
});

// 2.9 Получение всех папок
db.folders.find();

// 2.10 Поиск папок конкретного пользователя
db.folders.find({ userId: ObjectId("507f1f77bcf86cd799439011") });

// 2.11 Поиск папок по имени ($regex)
db.folders.find({
  name: { $regex: "Inbox", $options: "i" }
});

// 2.12 Получение всех писем в папке
db.messages.find({ folderId: ObjectId("507f1f77bcf86cd799439012") });

// 2.13 Получение письма по ID
db.messages.findOne({ _id: ObjectId("507f1f77bcf86cd799439013") });

// 2.14 Поиск писем от определённого отправителя
db.messages.find({ sender: "admin@email.com" });

// 2.15 Поиск писем для определённого получателя
db.messages.find({ recipient: "john.doe@email.com" });

// 2.16 Поиск писем по теме ($regex)
db.messages.find({
  subject: { $regex: "Meeting", $options: "i" }
});

// 2.17 Поиск писем за определённый период
db.messages.find({
  createdAt: {
    $gte: new Date("2025-01-15T00:00:00Z"),
    $lte: new Date("2025-01-17T23:59:59Z")
  }
});

// 2.18 Сложный поиск: письма от определённого отправителя в определённой папке ($and)
db.messages.find({
  $and: [
    { folderId: ObjectId("507f1f77bcf86cd799439012") },
    { sender: "admin@email.com" }
  ]
});

// 2.19 Поиск писем с определёнными темами ($or)
db.messages.find({
  $or: [
    { subject: { $regex: "Meeting" } },
    { subject: { $regex: "Project" } }
  ]
});

// 2.20 Поиск с сортировкой по дате (новые первыми)
db.messages.find({ folderId: ObjectId("507f1f77bcf86cd799439012") })
  .sort({ createdAt: -1 });

// 2.21 Поиск с лимитом (пагинация)
db.messages.find({ folderId: ObjectId("507f1f77bcf86cd799439012") })
  .sort({ createdAt: -1 })
  .limit(10)
  .skip(0);

// ============================================================================
// 3. UPDATE (Обновление документов)
// ============================================================================

// 3.1 Обновление пользователя по ID ($set)
db.users.updateOne(
  { _id: ObjectId("507f1f77bcf86cd799439011") },
  { $set: { firstName: "Jonathan", lastName: "Doe" } }
);

// 3.2 Обновление логина пользователя
db.users.updateOne(
  { login: "old.login" },
  { $set: { login: "new.login" } }
);

// 3.3 Обновление папки
db.folders.updateOne(
  { _id: ObjectId("507f1f77bcf86cd799439012") },
  { $set: { name: "Updated Inbox" } }
);

// 3.4 Обновление письма
db.messages.updateOne(
  { _id: ObjectId("507f1f77bcf86cd799439013") },
  { 
    $set: { 
      subject: "Updated Subject",
      body: "Updated message body"
    } 
  }
);

// 3.5 Обновление нескольких документов ($set)
db.folders.updateMany(
  { userId: ObjectId("507f1f77bcf86cd799439011") },
  { $set: { updatedAt: new Date() } }
);

// 3.6 Инкремент числового поля ($inc) - если бы использовали счётчики
db.users.updateOne(
  { login: "john.doe" },
  { $inc: { loginCount: 1 } }
);

// 3.7 Добавление элемента в массив ($push) - для тегов или меток
db.messages.updateOne(
  { _id: ObjectId("507f1f77bcf86cd799439013") },
  { $push: { tags: "important" } }
);

// 3.8 Добавление уникального элемента в массив ($addToSet)
db.messages.updateOne(
  { _id: ObjectId("507f1f77bcf86cd799439013") },
  { $addToSet: { tags: "urgent" } }
);

// 3.9 Удаление элемента из массива ($pull)
db.messages.updateOne(
  { _id: ObjectId("507f1f77bcf86cd799439013") },
  { $pull: { tags: "old" } }
);

// 3.10 Обновление с условием ($gt)
db.messages.updateMany(
  { createdAt: { $lt: new Date("2025-01-01T00:00:00Z") } },
  { $set: { archived: true } }
);

// 3.11 Переименование поля ($rename)
db.users.updateMany(
  {},
  { $rename: { "lastName": "familyName" } }
);

// 3.12 Удаление поля ($unset)
db.users.updateMany(
  {},
  { $unset: { temporaryField: "" } }
);

// ============================================================================
// 4. DELETE (Удаление документов)
// ============================================================================

// 4.1 Удаление пользователя по логину
db.users.deleteOne({ login: "test.user" });

// 4.2 Удаление пользователя по ID
db.users.deleteOne({ _id: ObjectId("507f1f77bcf86cd799439011") });

// 4.3 Удаление папки по ID
db.folders.deleteOne({ _id: ObjectId("507f1f77bcf86cd799439012") });

// 4.4 Удаление письма по ID
db.messages.deleteOne({ _id: ObjectId("507f1f77bcf86cd799439013") });

// 4.5 Удаление всех папок пользователя (каскадное удаление)
db.folders.deleteMany({ userId: ObjectId("507f1f77bcf86cd799439011") });

// 4.6 Удаление всех писем из папки
db.messages.deleteMany({ folderId: ObjectId("507f1f77bcf86cd799439012") });

// 4.7 Удаление старых писем (старше определённой даты)
db.messages.deleteMany({
  createdAt: { $lt: new Date("2024-01-01T00:00:00Z") }
});

// 4.8 Удаление пользователей с определённым доменом почты ($regex)
db.users.deleteMany({
  login: { $regex: "@temp\\.com$" }
});

// ============================================================================
// 5. АГРЕГАЦИИ (Aggregation Pipeline)
// ============================================================================

// 5.1 Подсчёт количества писем в каждой папке пользователя
db.folders.aggregate([
  { $match: { userId: ObjectId("507f1f77bcf86cd799439011") } },
  {
    $lookup: {
      from: "messages",
      localField: "_id",
      foreignField: "folderId",
      as: "messages"
    }
  },
  {
    $project: {
      name: 1,
      messageCount: { $size: "$messages" },
      lastMessageDate: { $max: "$messages.createdAt" }
    }
  },
  { $sort: { messageCount: -1 } }
]);

// 5.2 Статистика по пользователям: количество папок и писем
db.users.aggregate([
  {
    $lookup: {
      from: "folders",
      localField: "_id",
      foreignField: "userId",
      as: "folders"
    }
  },
  { $unwind: "$folders" },
  {
    $lookup: {
      from: "messages",
      localField: "folders._id",
      foreignField: "folderId",
      as: "folders.messages"
    }
  },
  {
    $group: {
      _id: "$_id",
      login: { $first: "$login" },
      totalFolders: { $sum: 1 },
      totalMessages: { $sum: { $size: "$folders.messages" } }
    }
  },
  { $sort: { totalMessages: -1 } }
]);

// 5.3 Поиск самых активных отправителей
db.messages.aggregate([
  {
    $group: {
      _id: "$sender",
      messageCount: { $sum: 1 },
      lastMessage: { $max: "$createdAt" }
    }
  },
  { $sort: { messageCount: -1 } },
  { $limit: 10 }
]);

// 5.4 Статистика по дням: количество писем за каждый день
db.messages.aggregate([
  {
    $group: {
      _id: {
        year: { $year: "$createdAt" },
        month: { $month: "$createdAt" },
        day: { $dayOfMonth: "$createdAt" }
      },
      messageCount: { $sum: 1 }
    }
  },
  { $sort: { "_id.year": -1, "_id.month": -1, "_id.day": -1 } }
]);

// 5.5 Поиск пользователей без папок
db.users.aggregate([
  {
    $lookup: {
      from: "folders",
      localField: "_id",
      foreignField: "userId",
      as: "folders"
    }
  },
  { $match: { folders: { $size: 0 } } },
  { $project: { login: 1, firstName: 1, lastName: 1 } }
]);

// 5.6 Полный отчёт по папке с письмами
db.folders.aggregate([
  { $match: { _id: ObjectId("507f1f77bcf86cd799439012") } },
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "owner"
    }
  },
  { $unwind: "$owner" },
  {
    $lookup: {
      from: "messages",
      localField: "_id",
      foreignField: "folderId",
      as: "messages"
    }
  },
  {
    $project: {
      name: 1,
      "owner.login": 1,
      "owner.firstName": 1,
      "owner.lastName": 1,
      messageCount: { $size: "$messages" },
      messages: {
        subject: 1,
        sender: 1,
        recipient: 1,
        createdAt: 1
      }
    }
  }
]);

// ============================================================================
// 6. ИНДЕКСЫ (Indexes)
// ============================================================================

// 6.1 Создание уникального индекса на login
db.users.createIndex({ login: 1 }, { unique: true });

// 6.2 Составной индекс для поиска по имени
db.users.createIndex({ firstName: 1, lastName: 1 });

// 6.3 Индекс для поиска папок пользователя
db.folders.createIndex({ userId: 1 });

// 6.4 Индекс для поиска писем в папке
db.messages.createIndex({ folderId: 1 });

// 6.5 Индекс для сортировки по дате
db.messages.createIndex({ createdAt: -1 });

// 6.6 Индекс для поиска по отправителю
db.messages.createIndex({ sender: 1 });

// 6.7 Индекс для поиска по получателю
db.messages.createIndex({ recipient: 1 });

// 6.8 Текстовый индекс для поиска по теме и телу письма
db.messages.createIndex({ subject: "text", body: "text" });

// 6.9 Просмотр всех индексов
db.users.getIndexes();
db.folders.getIndexes();
db.messages.getIndexes();

// ============================================================================
// 7. ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ В API
// ============================================================================

// 7.1 Регистрация пользователя (POST /api/auth/register)
// Вставка нового пользователя с хэшем пароля
db.users.insertOne({
  login: "newuser",
  firstName: "New",
  lastName: "User",
  password_hash: "$5$rounds=535000$...",
  createdAt: new Date()
});

// 7.2 Логин (POST /api/auth/login)
// Поиск пользователя по логину
db.users.findOne({ login: "newuser" });

// 7.3 Поиск пользователя по логину (GET /api/users/login/{login})
db.users.findOne({ login: "john.doe" });

// 7.4 Поиск по маске имени (GET /api/users/search?firstName=John&lastName=Doe)
db.users.find({
  $and: [
    { firstName: { $regex: "John", $options: "i" } },
    { lastName: { $regex: "Doe", $options: "i" } }
  ]
});

// 7.5 Создание папки (POST /api/folders)
db.folders.insertOne({
  name: "Inbox",
  userId: ObjectId("507f1f77bcf86cd799439011"),
  createdAt: new Date()
});

// 7.6 Получение всех папок (GET /api/folders)
db.folders.find();

// 7.7 Создание письма (POST /api/folders/{folder_id}/messages)
db.messages.insertOne({
  folderId: ObjectId("507f1f77bcf86cd799439012"),
  subject: "Hello",
  body: "This is a test message",
  sender: "sender@email.com",
  recipient: "recipient@email.com",
  createdAt: new Date()
});

// 7.8 Получение всех писем в папке (GET /api/folders/{folder_id}/messages)
db.messages.find({ folderId: ObjectId("507f1f77bcf86cd799439012") })
  .sort({ createdAt: -1 });

// 7.9 Получение письма по ID (GET /api/messages/{message_id})
db.messages.findOne({ _id: ObjectId("507f1f77bcf86cd799439013") });
