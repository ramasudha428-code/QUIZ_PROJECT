import json
import os
from sqlalchemy import select, func
from .session import SessionLocal
from .models import Question, User, AssessmentResult

DATA_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "python_questions.json")

# Helper to convert Question model to dict
def get_all_questions():
    with SessionLocal() as session:
        stmt = select(Question)
        results = session.execute(stmt).scalars().all()
        return [q.to_dict() for q in results]


def seed_questions_from_json():
    if not os.path.exists(DATA_JSON_PATH):
        return False

    with SessionLocal() as session:
        count = session.execute(select(func.count()).select_from(Question)).scalar_one()
        if count > 0:
            return False

        try:
            with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
        except Exception:
            return False

        for q in questions_data:
            question_text = q.get('question', '').strip()
            options = q.get('options', [])
            answer = q.get('answer', '').strip()
            topic = q.get('topic', 'General').strip() or 'General'
            if not question_text or not options or not answer:
                continue
            question = Question(
                question=question_text,
                options=json.dumps(options),
                answer=answer,
                topic=topic
            )
            session.add(question)

        session.commit()
    return True


def get_or_create_user(name: str):
    normalized = name.strip()
    if not normalized:
        return None

    with SessionLocal() as session:
        stmt = select(User).where(User.name == normalized)
        user = session.execute(stmt).scalar_one_or_none()
        if user:
            return user.id
        new_user = User(name=normalized)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user.id


def save_result(name: str, score: int, percentage: float, grade: str, weak_topics, feedback: str, user_id: int = None):
    """Save the assessment result with a linked user record."""
    weak_topics_json = json.dumps(weak_topics or [])
    if user_id is None:
        user_id = get_or_create_user(name)
    else:
        with SessionLocal() as session:
            existing_user = session.get(User, user_id)
            if existing_user is None:
                user_id = get_or_create_user(name)

    if user_id is None:
        raise ValueError('User name is required to save results.')

    with SessionLocal() as session:
        result = AssessmentResult(
            user_id=user_id,
            score=score,
            percentage=percentage,
            grade=grade,
            weak_topics=weak_topics_json,
            feedback=feedback
        )
        session.add(result)
        session.commit()
        session.refresh(result)
        return result.id


def get_result(result_id: int):
    with SessionLocal() as session:
        stmt = select(AssessmentResult, User).join(User).where(AssessmentResult.id == result_id)
        row = session.execute(stmt).one_or_none()
        if row:
            assessment_result, user = row
            result_data = assessment_result.to_dict()
            result_data['candidate_name'] = user.name
            return result_data
        return None


def add_question(question_text: str, options: list, answer: str, topic: str):
    """Insert a new Question into the database.
    
    Args:
        question_text: The question prompt.
        options: List of option strings.
        answer: The correct answer string.
        topic: Topic/category of the question.
    """
    with SessionLocal() as session:
        q = Question(
            question=question_text,
            options=json.dumps(options),
            answer=answer,
            topic=topic
        )
        session.add(q)
        session.commit()
        session.refresh(q)
        return q.id


def get_all_results_with_users():
    with SessionLocal() as session:
        stmt = select(AssessmentResult, User).join(User).order_by(AssessmentResult.created_at.desc())
        results = session.execute(stmt).all()
        out = []
        for assessment_result, user in results:
            d = assessment_result.to_dict()
            d['candidate_name'] = user.name
            out.append(d)
        return out


def delete_result(result_id: int):
    with SessionLocal() as session:
        result = session.get(AssessmentResult, result_id)
        if result:
            session.delete(result)
            session.commit()
            return True
        return False


def update_question(question_id: int, question_text: str, options: list, answer: str, topic: str):
    with SessionLocal() as session:
        q = session.get(Question, question_id)
        if q:
            q.question = question_text.strip()
            q.options = json.dumps(options)
            q.answer = answer.strip()
            q.topic = topic.strip() or 'General'
            session.commit()
            return True
        return False


def delete_question(question_id: int):
    with SessionLocal() as session:
        q = session.get(Question, question_id)
        if q:
            session.delete(q)
            session.commit()
            return True
        return False


def get_dashboard_stats():
    with SessionLocal() as session:
        # Total attempts
        total_attempts = session.execute(select(func.count()).select_from(AssessmentResult)).scalar_one()
        
        if total_attempts == 0:
            return {
                'total_attempts': 0,
                'avg_score': 0,
                'high_score': 0,
                'grade_distribution': {},
                'weak_topics_count': {}
            }

        # Average score (percentage)
        avg_score = session.execute(select(func.avg(AssessmentResult.percentage))).scalar_one() or 0.0
        
        # High score
        high_score = session.execute(select(func.max(AssessmentResult.percentage))).scalar_one() or 0.0

        # Grade distribution
        grade_stmt = select(AssessmentResult.grade, func.count()).group_by(AssessmentResult.grade)
        grade_dist = dict(session.execute(grade_stmt).all())

        # Weak topics count
        weak_stmt = select(AssessmentResult.weak_topics)
        weak_rows = session.execute(weak_stmt).scalars().all()
        
        weak_topics_count = {}
        for row in weak_rows:
            try:
                topics = json.loads(row)
                for t in topics:
                    t_str = str(t).strip()
                    if t_str:
                        weak_topics_count[t_str] = weak_topics_count.get(t_str, 0) + 1
            except Exception:
                pass

        return {
            'total_attempts': total_attempts,
            'avg_score': round(float(avg_score), 2),
            'high_score': round(float(high_score), 2),
            'grade_distribution': grade_dist,
            'weak_topics_count': weak_topics_count
        }


