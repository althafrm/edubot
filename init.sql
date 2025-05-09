CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

INSERT INTO courses (name) VALUES
('Computer Science'), ('Business Management'),
('Psychology'), ('Engineering'), ('Graphic Design');

CREATE TABLE IF NOT EXISTS knowledge (
    question TEXT PRIMARY KEY,
    answer TEXT NOT NULL
);

INSERT INTO knowledge (question, answer) VALUES
('what is ai', 'AI stands for Artificial Intelligence.'),
('what is education', 'Education is the process of acquiring knowledge.');

CREATE TABLE IF NOT EXISTS learned (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    timestamp TEXT
);
