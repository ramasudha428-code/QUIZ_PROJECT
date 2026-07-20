import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "quiz.db")
JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "python_questions.json")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            options TEXT NOT NULL, -- JSON string array of options
            answer TEXT NOT NULL,
            topic TEXT NOT NULL
        )
    ''')
    
    # Create users table for quiz candidates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create assessment_results table for user performance data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessment_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            percentage REAL NOT NULL,
            grade TEXT NOT NULL,
            weak_topics TEXT NOT NULL,
            feedback TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Create legacy results table for compatibility
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            percentage REAL NOT NULL,
            grade TEXT NOT NULL,
            weak_topics TEXT NOT NULL, -- JSON string list of weak topics
            feedback TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Populate questions if empty
    cursor.execute('SELECT COUNT(*) FROM questions')
    count = cursor.fetchone()[0]
    if count == 0:
        if os.path.exists(JSON_PATH):
            try:
                with open(JSON_PATH, 'r', encoding='utf-8') as f:
                    questions_data = json.load(f)
                for q in questions_data:
                    cursor.execute('''
                        INSERT INTO questions (question, options, answer, topic)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        q['question'],
                        json.dumps(q['options']),
                        q['answer'],
                        q.get('topic', 'General')
                    ))
                conn.commit()
                print("Questions table populated successfully from JSON.")
            except Exception as e:
                print(f"Error seeding database questions: {e}")
        else:
            print(f"JSON path not found at {JSON_PATH}. Skipping seed.")
            
    conn.close()

def get_all_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, question, options, answer, topic FROM questions')
    rows = cursor.fetchall()
    
    questions = []
    for row in rows:
        questions.append({
            'id': row['id'],
            'question': row['question'],
            'options': json.loads(row['options']),
            'answer': row['answer'],
            'topic': row['topic']
        })
    conn.close()
    return questions

def save_result(name, score, percentage, grade, weak_topics, feedback):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO results (candidate_name, score, percentage, grade, weak_topics, feedback)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        name,
        score,
        percentage,
        grade,
        json.dumps(weak_topics),
        feedback
    ))
    conn.commit()
    result_id = cursor.lastrowid
    conn.close()
    return result_id

def get_result(result_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM results WHERE id = ?', (result_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row['id'],
            'candidate_name': row['candidate_name'],
            'score': row['score'],
            'percentage': row['percentage'],
            'grade': row['grade'],
            'weak_topics': json.loads(row['weak_topics']),
            'feedback': row['feedback'],
            'timestamp': row['timestamp']
        }
    return None
