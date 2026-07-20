from database.queries import get_all_questions, seed_questions_from_json

def load_questions():
    """Load quiz questions from the SQLite database and seed them if needed."""
    questions = get_all_questions()
    if not questions:
        seed_questions_from_json()
        questions = get_all_questions()
    return questions
