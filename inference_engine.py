import json
import sqlite3
import re
import string

DB_PATH = "database/knowledge.db"
LEARN_FILE = "learn.json"

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM courses')
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO courses (name) VALUES (?)", [
            ("Computer Science",),
            ("Business Management",),
            ("Psychology",),
            ("Engineering",),
            ("Graphic Design",),
        ])
    conn.commit()
    conn.close()

init_database()

def load_learned_data():
    try:
        with open(LEARN_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_learned_data(data):
    with open(LEARN_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_db_courses():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM courses")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def preprocess(text):
    text = text.lower()
    text = text.replace("what's", "what is")
    text = text.replace("whats", "what is")
    text = text.replace("can't", "cannot")
    text = text.replace("won't", "will not")
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.strip()

def process_input(user_input):
    raw_input = user_input
    user_input = preprocess(user_input)

    if raw_input.lower().startswith("add:"):
        try:
            _, pair = raw_input.split("add:", 1)
            question, answer = pair.split("=", 1)
            question = preprocess(question.strip())
            answer = answer.strip()
            learned = load_learned_data()
            learned[question] = answer
            save_learned_data(learned)
            return "Learned successfully!"
        except:
            return "Invalid format. Use: Add: What is AI? = Artificial Intelligence"

    learned = load_learned_data()

    for key in learned:
        if preprocess(key) == user_input:
            return learned[key]

    if re.search(r'course|degree|offer', user_input):
        return "We offer: " + ", ".join(get_db_courses())

    elif re.search(r'how.*(apply|join|enroll|register)', user_input):
        return "To join a course, please visit our admissions page and submit your application form."

    elif "deadline" in user_input:
        return "The application deadline is June 30."

    elif "requirement" in user_input:
        return "You need at least 3 A-levels or equivalent qualifications."

    elif "hello" in user_input or "hi" in user_input:
        return "Hello! How can I assist you with your education queries?"

    elif "thank" in user_input:
        return "You're welcome!"

    return "Sorry, I don't understand that. You can teach me using: Add: question = answer"
