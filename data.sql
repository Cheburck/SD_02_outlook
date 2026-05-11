INSERT INTO users (login, first_name, last_name, password_hash) VALUES
('john.doe', 'John', 'Doe', '$5$rounds=535000$abc123$hashed_password_1'),
('jane.smith', 'Jane', 'Smith', '$5$rounds=535000$abc123$hashed_password_2'),
('bob.wilson', 'Bob', 'Wilson', '$5$rounds=535000$abc123$hashed_password_3'),
('alice.johnson', 'Alice', 'Johnson', '$5$rounds=535000$abc123$hashed_password_4'),
('charlie.brown', 'Charlie', 'Brown', '$5$rounds=535000$abc123$hashed_password_5'),
('diana.prince', 'Diana', 'Prince', '$5$rounds=535000$abc123$hashed_password_6'),
('edward.norton', 'Edward', 'Norton', '$5$rounds=535000$abc123$hashed_password_7'),
('fiona.green', 'Fiona', 'Green', '$5$rounds=535000$abc123$hashed_password_8'),
('george.harris', 'George', 'Harris', '$5$rounds=535000$abc123$hashed_password_9'),
('helen.clark', 'Helen', 'Clark', '$5$rounds=535000$abc123$hashed_password_10');

INSERT INTO folders (name, user_id) VALUES
('Documents', 1),
('Photos', 1),
('Work', 2),
('Personal', 2),
('Projects', 3),
('Archive', 3),
('Reports', 4),
('Images', 5),
('Music', 6),
('Videos', 7),
('Backups', 8),
('Downloads', 9),
('Uploads', 10);

INSERT INTO messages (folder_id, subject, body, sender, recipient) VALUES
(1, 'report.pdf', 'Annual financial report content', 'john.doe', 'jane.smith'),
(1, 'budget.xlsx', 'Budget spreadsheet data', 'john.doe', 'bob.wilson'),
(2, 'vacation.jpg', 'Photo from vacation', 'john.doe', 'alice.johnson'),
(3, 'presentation.pptx', 'Q4 presentation slides', 'jane.smith', 'charlie.brown'),
(3, 'meeting_notes.docx', 'Notes from team meeting', 'jane.smith', 'diana.prince'),
(4, 'resume.pdf', 'Updated resume document', 'jane.smith', 'edward.norton'),
(5, 'project_plan.md', 'Project planning document', 'bob.wilson', 'fiona.green'),
(6, 'old_data.csv', 'Archived data from 2023', 'bob.wilson', 'george.harris'),
(7, 'monthly_report.pdf', 'Monthly status report', 'alice.johnson', 'helen.clark'),
(8, 'photo_album.zip', 'Collection of photos', 'charlie.brown', 'john.doe'),
(9, 'playlist.m3u', 'Music playlist file', 'diana.prince', 'jane.smith'),
(10, 'tutorial.mp4', 'Video tutorial content', 'edward.norton', 'alice.johnson'),
(11, 'backup_2024.tar.gz', 'System backup archive', 'fiona.green', 'bob.wilson'),
(12, 'installer.exe', 'Software installer file', 'george.harris', 'charlie.brown'),
(13, 'dataset.csv', 'Upload dataset for analysis', 'helen.clark', 'diana.prince');
