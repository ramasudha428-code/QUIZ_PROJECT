from flask import Flask, render_template, request, jsonify, redirect, url_for
import os

# Import database utilities
from database.queries import (
    get_all_questions, save_result as save_db_result, get_or_create_user, get_result, seed_questions_from_json,
    get_all_results_with_users, delete_result, add_question, update_question, delete_question, get_dashboard_stats
)
from database.session import engine
from database.models import Base
from quiz_app.chatbot import process_chat_message
from quiz_app.score_manager import calculate_percentage, generate_grade
from quiz_app.ai_tools import generate_ai_question, modify_ai_question

# Helper: generate feedback string based on quiz performance
def chatbot_feedback(percentage, weak_topics):
    """Return a feedback message for the user.
    Args:
        percentage (float): The score percentage.
        weak_topics (list): List of topic strings the user struggled with.
    Returns:
        str: Human‑readable feedback.
    """
    if weak_topics:
        unique = sorted(set(weak_topics))
        topics_str = ", ".join(unique)
        return f"You scored {percentage:.2f}%. Review these topics: {topics_str}."
    return f"You scored {percentage:.2f}%. Good job!"

# Helper: write a simple text report for the candidate
def save_txt_result(candidate_name, score, percentage, grade, directory="reports"):
    """Save a plain‑text quiz report.
    The file is named `<candidate_name>_result.txt` under the given directory.
    """
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"{candidate_name.replace(' ', '_')}_result.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Candidate: {candidate_name}\n")
        f.write(f"Score: {score}\n")
        f.write(f"Percentage: {percentage:.2f}%\n")
        f.write(f"Grade: {grade}\n")
    # Return path for potential further use
    return filename


app = Flask(__name__)

# Initialize database tables with SQLAlchemy
try:
    Base.metadata.create_all(bind=engine)
    # Seed static assessment questions from JSON if the database is empty
    seed_questions_from_json()
    print("Database tables initialized and seeded successfully.")
except Exception as e:
    print("WARNING: Could not connect to database or initialize tables!")
    print(f"Details: {e}")
    print("Continuing startup. Please verify DB_URL in .env is correct and PostgreSQL is running.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def api_start():
    data = request.get_json(silent=True)
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400

    candidate_name = str(data.get('name', '')).strip()
    if not candidate_name:
        return jsonify({'error': 'Name cannot be empty'}), 400

    user_id = get_or_create_user(candidate_name)
    if user_id is None:
        return jsonify({'error': 'Unable to create user'}), 500

    return jsonify({'status': 'success', 'user_id': user_id})


@app.route('/api/questions', methods=['GET'])
def api_questions():
    questions = get_all_questions()
    # Strip correct answers to prevent user cheating by inspecting the network traffic.
    client_questions = []
    for q in questions:
        client_questions.append({
            'id': q['id'],
            'question': q['question'],
            'options': q['options'],
            'topic': q['topic']
        })
    return jsonify(client_questions)

@app.route('/api/submit', methods=['POST'])
def api_submit():
    data = request.get_json(silent=True)
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400

    candidate_name = str(data.get('name', '')).strip()
    if not candidate_name:
        return jsonify({'error': 'Name cannot be empty'}), 400

    user_answers = data.get('answers', {})
    if not isinstance(user_answers, dict):
        user_answers = {}

    questions = get_all_questions()
    total_questions = len(questions)
    score = 0
    weak_topics = []
    user_id = data.get('user_id')

    for q in questions:
        q_id_str = str(q['id'])
        selected_ans = user_answers.get(q_id_str, "")
        
        correct_ans = q['answer']
        if str(selected_ans).strip().lower() == str(correct_ans).strip().lower():
            score += 1
        else:
            weak_topics.append(q['topic'])
            
    percentage = calculate_percentage(score, total_questions)
    grade = generate_grade(percentage)
    feedback = chatbot_feedback(percentage, weak_topics)
    
    # Save to database
    result_id = save_db_result(
        name=candidate_name,
        score=score,
        percentage=percentage,
        grade=grade,
        weak_topics=weak_topics,
        feedback=feedback,
        user_id=user_id if isinstance(user_id, int) else None
    )
    
    # Save to local text report file
    save_txt_result(candidate_name, score, percentage, grade)
    
    return jsonify({
        'status': 'success',
        'result_id': result_id
    })

@app.route('/result/<int:result_id>')
def view_result(result_id):
    result_data = get_result(result_id)
    if not result_data:
        return redirect(url_for('index'))
        
    questions = get_all_questions()
    total_questions = len(questions)
    
    return render_template('result.html', result=result_data, total_questions=total_questions)


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Real-time chatbot API — accepts user message + optional quiz context."""
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    context = {
        'candidate_name': data.get('candidate_name', ''),
        'score': data.get('score'),
        'grade': data.get('grade'),
        'weak_topics': data.get('weak_topics', []),
    }

    response_text = process_chat_message(user_message, context)
    return jsonify({'reply': response_text})


# ════════════════════════════════════════════════════════════════
# ADMIN API ENDPOINTS
# ════════════════════════════════════════════════════════════════

@app.route('/admin')
def admin():
    """Admin Dashboard Page."""
    return render_template('admin.html')

@app.route('/api/admin/stats', methods=['GET'])
def api_admin_stats():
    """Get aggregated statistics of candidate attempts."""
    try:
        stats = get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/results', methods=['GET'])
def api_admin_results():
    """Get list of all candidate attempt results."""
    try:
        results = get_all_results_with_users()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/results/<int:result_id>', methods=['DELETE'])
def api_admin_delete_result(result_id):
    """Delete a specific candidate result."""
    try:
        success = delete_result(result_id)
        if success:
            return jsonify({'status': 'success', 'message': 'Result deleted successfully.'})
        return jsonify({'error': 'Result not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/questions', methods=['GET'])
def api_admin_questions():
    """Get list of all questions with full details (for admin management)."""
    try:
        questions = get_all_questions()
        return jsonify(questions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/questions', methods=['POST'])
def api_admin_create_question():
    """Create a new question in the database."""
    try:
        data = request.get_json(silent=True) or {}
        question_text = data.get('question', '').strip()
        options = data.get('options', [])
        answer = data.get('answer', '').strip()
        topic = data.get('topic', 'General').strip()

        if not question_text or not options or not answer:
            return jsonify({'error': 'Question text, options, and correct answer are required.'}), 400

        if not isinstance(options, list) or len(options) < 2:
            return jsonify({'error': 'At least 2 options are required.'}), 400

        # Validate that the answer exists in the options
        if answer not in options:
            return jsonify({'error': 'Correct answer must be one of the options.'}), 400

        q_id = add_question(question_text, options, answer, topic)
        return jsonify({'status': 'success', 'question_id': q_id, 'message': 'Question created successfully.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/questions/<int:q_id>', methods=['PUT'])
def api_admin_update_question(q_id):
    """Update an existing question in the database."""
    try:
        data = request.get_json(silent=True) or {}
        question_text = data.get('question', '').strip()
        options = data.get('options', [])
        answer = data.get('answer', '').strip()
        topic = data.get('topic', 'General').strip()

        if not question_text or not options or not answer:
            return jsonify({'error': 'Question text, options, and correct answer are required.'}), 400

        if not isinstance(options, list) or len(options) < 2:
            return jsonify({'error': 'At least 2 options are required.'}), 400

        # Validate that the answer exists in the options
        if answer not in options:
            return jsonify({'error': 'Correct answer must be one of the options.'}), 400

        success = update_question(q_id, question_text, options, answer, topic)
        if success:
            return jsonify({'status': 'success', 'message': 'Question updated successfully.'})
        return jsonify({'error': 'Question not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/questions/<int:q_id>', methods=['DELETE'])
def api_admin_delete_question(q_id):
    """Delete a question from the database."""
    try:
        success = delete_question(q_id)
        if success:
            return jsonify({'status': 'success', 'message': 'Question deleted successfully.'})
        return jsonify({'error': 'Question not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/ai/generate', methods=['POST'])
def api_admin_ai_generate():
    """Generate a new question using Google Gemini AI."""
    try:
        data = request.get_json(silent=True) or {}
        topic = data.get('topic', 'General').strip() or 'General'
        difficulty = data.get('difficulty', 'Intermediate').strip() or 'Intermediate'
        prompt = data.get('prompt', '').strip()

        question_data = generate_ai_question(topic, difficulty, prompt)
        return jsonify(question_data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/ai/modify', methods=['POST'])
def api_admin_ai_modify():
    """Modify an existing question using Google Gemini AI."""
    try:
        data = request.get_json(silent=True) or {}
        question = data.get('question', '').strip()
        options = data.get('options', [])
        answer = data.get('answer', '').strip()
        topic = data.get('topic', 'General').strip() or 'General'
        instruction = data.get('instruction', '').strip()

        if not question or not options or not answer or not instruction:
            return jsonify({'error': 'Question fields and modification instructions are required.'}), 400

        if not isinstance(options, list) or len(options) < 2:
            return jsonify({'error': 'Question must have options.'}), 400

        modified_data = modify_ai_question(question, options, answer, topic, instruction)
        return jsonify(modified_data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)
