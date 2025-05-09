import re
import random
import sqlite3
import nltk
from nltk.stem import WordNetLemmatizer
from datetime import datetime

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

lemmatizer = WordNetLemmatizer()
DB_PATH = "database/knowledge.db"

# Synonym mapping
SYNONYMS = {
    "register": ["enroll", "join", "apply", "sign up"],
    "course": ["module", "subject", "program", "degree"],
    "computer science": ["comp sci", "cs", "cs course"],
    "hello": ["hi", "hey", "greetings"],
    "thanks": ["thank you", "cheers"],
    "bye": ["goodbye", "see you"]
}

# Build reverse synonym lookup
def build_synonym_lookup(synonyms):
    mapping = {}
    for key, values in synonyms.items():
        for word in values + [key]:
            mapping[word] = key
    return mapping

SYN_LOOKUP = build_synonym_lookup(SYNONYMS)

# Small talk responses
SMALLTALK = {
    "hello": ["Hello there!", "Hi, how can I help you?", "Greetings!"],
    "how are you": ["I'm great!", "Doing well. How can I assist you?", "I'm fine, thank you!"],
    "who are you": ["I'm EduBot, your course assistant."],
    "bye": ["Goodbye!", "See you soon!", "Take care!"],
    "thanks": ["You're welcome!", "No problem!", "Happy to help!"],
    "ok": ["Great!", "Okay then.", "Understood."]
}

# Normalize and canonicalize input
def normalize_input(user_input):
    user_input = user_input.lower()
    user_input = re.sub(r"[^\w\s]", "", user_input)

    # Replace full phrases before splitting
    for phrase in sorted(SYN_LOOKUP, key=lambda x: -len(x.split())):
        if phrase in user_input:
            user_input = user_input.replace(phrase, SYN_LOOKUP[phrase])

    words = user_input.split()
    canonical = [SYN_LOOKUP.get(lemmatizer.lemmatize(w), lemmatizer.lemmatize(w)) for w in words]
    return " ".join(canonical)

# Generate answer for user input
def get_answer(user_input):
    norm = normalize_input(user_input)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check learned data
    cursor.execute("SELECT answer FROM learned WHERE question = ?", (norm,))
    row = cursor.fetchone()
    if row:
        return row[0]

    # Check small talk
    for phrase, responses in SMALLTALK.items():
        if phrase in norm:
            return random.choice(responses)

    # Check static knowledge
    cursor.execute("SELECT answer FROM knowledge WHERE question = ?", (norm,))
    row = cursor.fetchone()
    if row:
        return row[0]

    # Special case: enrollment intent + course
    enroll_keywords = ["enroll", "join", "register", "apply"]
    course_keywords = ["course", "computer science", "engineering", "business", "psychology", "graphic"]

    if any(k in norm for k in enroll_keywords):
        if any(k in norm for k in course_keywords):
            return "To enroll in that course, please visit our admissions page or contact the registrar."
        return "To enroll, please visit our admissions page or contact the registrar."

    # Special case: course listing
    if "course" in norm:
        cursor.execute("SELECT name FROM courses")
        rows = cursor.fetchall()
        course_list = [r[0] for r in rows]
        return "Our available courses are:\n- " + "\n- ".join(course_list)

    conn.close()

    # Fallback
    return random.choice([
        "Hmm, I’m not sure about that yet.",
        "Can you try asking in a different way?",
        "I'm still learning. Could you rephrase?"
    ])

# Learn a new Q&A
def learn(question, answer):
    norm = normalize_input(question)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO learned (question, answer, timestamp) VALUES (?, ?, ?)",
                   (norm, answer, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Initialize database on first run
def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            question TEXT PRIMARY KEY,
            answer TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learned (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp TEXT
        )
    ''')

    # Seed data
    cursor.execute('SELECT COUNT(*) FROM courses')
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO courses (name) VALUES (?)", [
            ("Computer Science",),
            ("Business Management",),
            ("Psychology",),
            ("Engineering",),
            ("Graphic Design",)
        ])

    cursor.execute('SELECT COUNT(*) FROM knowledge')
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO knowledge (question, answer) VALUES (?, ?)", [
            ("what is ai", "AI stands for Artificial Intelligence."),
            ("what is education", "Education is the process of acquiring knowledge.")
        ])

    conn.commit()
    conn.close()

# Run initializer immediately
init_database()
