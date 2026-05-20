-- Data for Email System (Outlook)
-- Тестовые данные для базы данных
-- Author: Sitdikov Risat M8O-102SV-25

-- ============================================
-- TABLE: users (12 пользователей)
-- ============================================
INSERT INTO users (login, password_hash, first_name, last_name) VALUES
('john.doe', '$5$rounds=535000$abc123$hashed_password_1', 'John', 'Doe'),
('jane.smith', '$5$rounds=535000$def456$hashed_password_2', 'Jane', 'Smith'),
('bob.wilson', '$5$rounds=535000$ghi789$hashed_password_3', 'Bob', 'Wilson'),
('alice.johnson', '$5$rounds=535000$jkl012$hashed_password_4', 'Alice', 'Johnson'),
('charlie.brown', '$5$rounds=535000$mno345$hashed_password_5', 'Charlie', 'Brown'),
('diana.prince', '$5$rounds=535000$pqr678$hashed_password_6', 'Diana', 'Prince'),
('edward.norton', '$5$rounds=535000$stu901$hashed_password_7', 'Edward', 'Norton'),
('fiona.green', '$5$rounds=535000$vwx234$hashed_password_8', 'Fiona', 'Green'),
('george.white', '$5$rounds=535000$yza567$hashed_password_9', 'George', 'White'),
('helen.black', '$5$rounds=535000$bcd890$hashed_password_10', 'Helen', 'Black'),
('ivan.petrov', '$5$rounds=535000$efg123$hashed_password_11', 'Ivan', 'Petrov'),
('maria.garcia', '$5$rounds=535000$hij456$hashed_password_12', 'Maria', 'Garcia');

-- ============================================
-- TABLE: folders (15 папок)
-- ============================================
INSERT INTO folders (name, user_id) VALUES
('Inbox', 1),
('Sent', 1),
('Drafts', 1),
('Spam', 1),
('Inbox', 2),
('Sent', 2),
('Work', 2),
('Personal', 3),
('Inbox', 3),
('Archive', 4),
('Inbox', 5),
('Sent', 5),
('Projects', 6),
('Inbox', 7),
('Notifications', 8);

-- ============================================
-- TABLE: messages (20 писем)
-- ============================================
INSERT INTO messages (folder_id, subject, body, sender, recipient) VALUES
(1, 'Welcome to Outlook', 'Hello! Welcome to our email service. We are glad to have you.', 'support@outlook.com', 'john.doe@email.com'),
(1, 'Meeting Tomorrow', 'Hi John, just a reminder about our meeting tomorrow at 10 AM.', 'jane.smith@email.com', 'john.doe@email.com'),
(1, 'Project Update', 'The project is progressing well. Please review the attached documents.', 'bob.wilson@email.com', 'john.doe@email.com'),
(2, 'Re: Meeting Tomorrow', 'Thanks for the reminder. I will be there.', 'john.doe@email.com', 'jane.smith@email.com'),
(2, 'Weekly Report', 'Here is the weekly report for your review.', 'john.doe@email.com', 'alice.johnson@email.com'),
(3, 'Draft: Proposal', 'This is a draft of the new project proposal...', 'john.doe@email.com', 'charlie.brown@email.com'),
(4, 'Special Offer', 'Get 50% off on all products! Limited time offer.', 'marketing@spam.com', 'john.doe@email.com'),
(5, 'Hello from Jane', 'Hi! How are you doing? Lets catch up soon.', 'alice.johnson@email.com', 'jane.smith@email.com'),
(5, 'Document Review', 'Please review the attached document and provide feedback.', 'diana.prince@email.com', 'jane.smith@email.com'),
(6, 'Re: Hello', 'Great to hear from you! Lets meet next week.', 'jane.smith@email.com', 'alice.johnson@email.com'),
(7, 'Q4 Planning', 'We need to start planning for Q4. Please prepare your reports.', 'edward.norton@email.com', 'jane.smith@email.com'),
(8, 'Weekend Plans', 'Hey Bob, want to go hiking this weekend?', 'fiona.green@email.com', 'bob.wilson@email.com'),
(9, 'Invoice #12345', 'Please find attached invoice for services rendered.', 'accounting@company.com', 'bob.wilson@email.com'),
(10, 'Archive: Old Project', 'Archiving old project documents for reference.', 'george.white@email.com', 'alice.johnson@email.com'),
(11, 'Team Building Event', 'Join us for the annual team building event next month.', 'hr@company.com', 'charlie.brown@email.com'),
(11, 'New Hire Orientation', 'Welcome to the team! Here is your orientation schedule.', 'hr@company.com', 'charlie.brown@email.com'),
(12, 'Re: Team Building', 'Count me in for the team building event!', 'charlie.brown@email.com', 'hr@company.com'),
(13, 'Project Alpha Status', 'Project Alpha is on track. Milestone 3 completed.', 'diana.prince@email.com', 'diana.prince@email.com'),
(14, 'System Notification', 'Your password was changed successfully.', 'security@outlook.com', 'edward.norton@email.com'),
(15, 'Newsletter #42', 'Check out our latest newsletter with exciting updates!', 'newsletter@company.com', 'fiona.green@email.com');

-- ============================================
-- Verification Queries
-- ============================================
-- SELECT 'users' as table_name, COUNT(*) as row_count FROM users
-- UNION ALL
-- SELECT 'folders', COUNT(*) FROM folders
-- UNION ALL
-- SELECT 'messages', COUNT(*) FROM messages;
