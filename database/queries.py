import json
import os
from collections import defaultdict
from datetime import datetime
from sqlalchemy import select, func, delete
from .session import SessionLocal, engine
from .models import Question, User, AssessmentResult

DATA_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "python_questions.json")

# ════════════════════════════════════════════════════════════════
# QUESTION QUERIES
# ════════════════════════════════════════════════════════════════

def get_all_questions():
    with SessionLocal() as session:
        stmt = select(Question).order_by(Question.id.asc())
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


def add_question(question_text: str, options: list, answer: str, topic: str):
    """Insert a single new Question into the database."""
    with SessionLocal() as session:
        q = Question(
            question=question_text.strip(),
            options=json.dumps(options),
            answer=answer.strip(),
            topic=topic.strip() or 'General'
        )
        session.add(q)
        session.commit()
        session.refresh(q)
        return q.id


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


def bulk_add_questions(questions_list: list):
    """Bulk insert questions with schema validation."""
    added = 0
    skipped = 0
    errors = []

    with SessionLocal() as session:
        for idx, item in enumerate(questions_list, 1):
            q_text = str(item.get('question', '')).strip()
            options = item.get('options', [])
            answer = str(item.get('answer', '')).strip()
            topic = str(item.get('topic', 'General')).strip() or 'General'

            if not q_text:
                errors.append(f"Row #{idx}: Missing question text.")
                skipped += 1
                continue

            if not isinstance(options, list) or len(options) < 2:
                errors.append(f"Row #{idx}: Must have at least 2 options.")
                skipped += 1
                continue

            if not answer:
                errors.append(f"Row #{idx}: Missing answer.")
                skipped += 1
                continue

            # Ensure answer matches one of the options (case-insensitive check with auto-sync)
            matched_answer = None
            for opt in options:
                if str(opt).strip().lower() == answer.lower():
                    matched_answer = str(opt).strip()
                    break

            if matched_answer is None:
                # If answer is 'A', 'B', 'C', 'D', map by index
                letter_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                if answer.upper() in letter_map and letter_map[answer.upper()] < len(options):
                    matched_answer = str(options[letter_map[answer.upper()]]).strip()
                else:
                    errors.append(f"Row #{idx}: Correct answer '{answer}' is not in options {options}.")
                    skipped += 1
                    continue

            clean_options = [str(o).strip() for o in options if str(o).strip()]
            q = Question(
                question=q_text,
                options=json.dumps(clean_options),
                answer=matched_answer,
                topic=topic
            )
            session.add(q)
            added += 1

        if added > 0:
            session.commit()

    return {
        'added_count': added,
        'skipped_count': skipped,
        'errors': errors
    }


def export_all_questions_data():
    with SessionLocal() as session:
        stmt = select(Question).order_by(Question.id.asc())
        questions = session.execute(stmt).scalars().all()
        return [q.to_dict() for q in questions]


# ════════════════════════════════════════════════════════════════
# USER / STUDENT QUERIES
# ════════════════════════════════════════════════════════════════

def get_or_create_user(name: str):
    normalized = name.strip()
    if not normalized:
        return None

    with SessionLocal() as session:
        stmt = select(User).where(func.lower(User.name) == normalized.lower())
        user = session.execute(stmt).scalar_one_or_none()
        if user:
            return user.id
        new_user = User(name=normalized)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user.id


def get_all_students():
    """Retrieve all students with their summarized performance metrics."""
    with SessionLocal() as session:
        users = session.execute(select(User).order_by(User.name.asc())).scalars().all()
        students_list = []

        for u in users:
            results = session.execute(
                select(AssessmentResult)
                .where(AssessmentResult.user_id == u.id)
                .order_by(AssessmentResult.created_at.desc())
            ).scalars().all()

            attempt_count = len(results)
            if attempt_count > 0:
                percentages = [r.percentage for r in results]
                avg_pct = round(sum(percentages) / attempt_count, 1)
                best_pct = round(max(percentages), 1)
                latest_res = results[0]
                latest_date = latest_res.created_at.isoformat() if latest_res.created_at else None
                latest_grade = latest_res.grade
                latest_score = latest_res.score

                # Calculate status
                if avg_pct >= 80:
                    status = "Excellent"
                elif avg_pct >= 60:
                    status = "Passing"
                elif avg_pct >= 40:
                    status = "Average"
                else:
                    status = "At-Risk"
            else:
                avg_pct = 0.0
                best_pct = 0.0
                latest_date = None
                latest_grade = "N/A"
                latest_score = 0
                status = "Not Started"

            students_list.append({
                "id": u.id,
                "name": u.name,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "attempt_count": attempt_count,
                "avg_percentage": avg_pct,
                "best_percentage": best_pct,
                "latest_score": latest_score,
                "latest_grade": latest_grade,
                "latest_attempt_date": latest_date,
                "status": status
            })

        return students_list


def get_student_detail(user_id: int):
    """Retrieve detailed profile, timeline, and topic analytics for a single student."""
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if not user:
            return None

        results = session.execute(
            select(AssessmentResult)
            .where(AssessmentResult.user_id == user_id)
            .order_by(AssessmentResult.created_at.asc())
        ).scalars().all()

        timeline = []
        weak_topics_frequency = defaultdict(int)

        for r in results:
            d = r.to_dict()
            timeline.append(d)
            for t in d.get("weak_topics", []):
                t_str = str(t).strip()
                if t_str:
                    weak_topics_frequency[t_str] += 1

        percentages = [r.percentage for r in results]
        attempt_count = len(results)
        avg_pct = round(sum(percentages) / attempt_count, 1) if attempt_count > 0 else 0.0
        best_pct = round(max(percentages), 1) if attempt_count > 0 else 0.0

        return {
            "id": user.id,
            "name": user.name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "attempt_count": attempt_count,
            "avg_percentage": avg_pct,
            "best_percentage": best_pct,
            "timeline": timeline,
            "weak_topics_breakdown": dict(weak_topics_frequency)
        }


def find_student_by_name(name: str):
    """Lookup student detail by candidate name for self-service portal."""
    normalized = name.strip()
    if not normalized:
        return None

    with SessionLocal() as session:
        stmt = select(User).where(func.lower(User.name) == normalized.lower())
        user = session.execute(stmt).scalar_one_or_none()
        if not user:
            return None
        return get_student_detail(user.id)


def delete_user_and_results(user_id: int):
    """Delete a student and cascade delete all their attempts."""
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            session.commit()
            return True
        return False


def reset_student_attempts(user_id: int):
    """Delete all attempts for a student while keeping the student account."""
    with SessionLocal() as session:
        stmt = delete(AssessmentResult).where(AssessmentResult.user_id == user_id)
        res = session.execute(stmt)
        session.commit()
        return res.rowcount >= 0


# ════════════════════════════════════════════════════════════════
# ASSESSMENT RESULT QUERIES
# ════════════════════════════════════════════════════════════════

def save_result(name: str, score: int, percentage: float, grade: str, weak_topics, feedback: str, user_id: int = None):
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


def clear_all_assessment_results():
    """Purge all candidate test results from database."""
    with SessionLocal() as session:
        session.execute(delete(AssessmentResult))
        session.commit()
        return True


# ════════════════════════════════════════════════════════════════
# DASHBOARD, PERFORMANCE & SYSTEM STATS
# ════════════════════════════════════════════════════════════════

def get_dashboard_stats():
    """High-level KPI stats for Admin Dashboard."""
    with SessionLocal() as session:
        total_attempts = session.execute(select(func.count()).select_from(AssessmentResult)).scalar_one()
        total_students = session.execute(select(func.count()).select_from(User)).scalar_one()
        total_questions = session.execute(select(func.count()).select_from(Question)).scalar_one()

        if total_attempts == 0:
            return {
                'total_attempts': 0,
                'total_students': total_students,
                'total_questions': total_questions,
                'avg_score': 0,
                'high_score': 0,
                'pass_rate': 0,
                'grade_distribution': {},
                'weak_topics_count': {}
            }

        avg_score = session.execute(select(func.avg(AssessmentResult.percentage))).scalar_one() or 0.0
        high_score = session.execute(select(func.max(AssessmentResult.percentage))).scalar_one() or 0.0

        # Calculate Pass Rate (Percentage >= 60%)
        pass_count = session.execute(
            select(func.count()).select_from(AssessmentResult).where(AssessmentResult.percentage >= 60.0)
        ).scalar_one()
        pass_rate = round((pass_count / total_attempts) * 100, 1)

        grade_stmt = select(AssessmentResult.grade, func.count()).group_by(AssessmentResult.grade)
        grade_dist = dict(session.execute(grade_stmt).all())

        weak_stmt = select(AssessmentResult.weak_topics)
        weak_rows = session.execute(weak_stmt).scalars().all()

        weak_topics_count = defaultdict(int)
        for row in weak_rows:
            try:
                topics = json.loads(row)
                for t in topics:
                    t_str = str(t).strip()
                    if t_str:
                        weak_topics_count[t_str] += 1
            except Exception:
                pass

        return {
            'total_attempts': total_attempts,
            'total_students': total_students,
            'total_questions': total_questions,
            'avg_score': round(float(avg_score), 1),
            'high_score': round(float(high_score), 1),
            'pass_rate': pass_rate,
            'grade_distribution': grade_dist,
            'weak_topics_count': dict(weak_topics_count)
        }


def get_comprehensive_performance_data():
    """Detailed analytics data for Chart.js and deep diagnostic reports."""
    with SessionLocal() as session:
        total_attempts = session.execute(select(func.count()).select_from(AssessmentResult)).scalar_one()
        total_students = session.execute(select(func.count()).select_from(User)).scalar_one()
        total_questions = session.execute(select(func.count()).select_from(Question)).scalar_one()

        if total_attempts == 0:
            return {
                'total_attempts': 0,
                'total_students': total_students,
                'total_questions': total_questions,
                'score_distribution': {'0-20%': 0, '21-40%': 0, '41-60%': 0, '61-80%': 0, '81-100%': 0},
                'grade_distribution': {},
                'topic_failure_rates': {},
                'timeline_trends': [],
                'leaderboard': [],
                'at_risk_students': []
            }

        # 1. Score Distribution Histogram (5 Bins)
        score_bins = {'0-20%': 0, '21-40%': 0, '41-60%': 0, '61-80%': 0, '81-100%': 0}
        percentages = session.execute(select(AssessmentResult.percentage)).scalars().all()
        for pct in percentages:
            if pct <= 20:
                score_bins['0-20%'] += 1
            elif pct <= 40:
                score_bins['21-40%'] += 1
            elif pct <= 60:
                score_bins['41-60%'] += 1
            elif pct <= 80:
                score_bins['61-80%'] += 1
            else:
                score_bins['81-100%'] += 1

        # 2. Grade Distribution
        grade_stmt = select(AssessmentResult.grade, func.count()).group_by(AssessmentResult.grade)
        grade_dist = dict(session.execute(grade_stmt).all())

        # 3. Topic Failure & Weakness Breakdown
        weak_stmt = select(AssessmentResult.weak_topics)
        weak_rows = session.execute(weak_stmt).scalars().all()
        topic_failures = defaultdict(int)
        for row in weak_rows:
            try:
                topics = json.loads(row)
                for t in topics:
                    t_str = str(t).strip()
                    if t_str:
                        topic_failures[t_str] += 1
            except Exception:
                pass

        # 4. Activity Trends by Date
        stmt = select(AssessmentResult.created_at, AssessmentResult.percentage).order_by(AssessmentResult.created_at.asc())
        date_rows = session.execute(stmt).all()
        trend_map = defaultdict(lambda: {'count': 0, 'total_score': 0.0})

        for created_at, pct in date_rows:
            if created_at:
                date_str = created_at.strftime('%Y-%m-%d')
                trend_map[date_str]['count'] += 1
                trend_map[date_str]['total_score'] += float(pct)

        timeline_trends = []
        for date_str, stats in sorted(trend_map.items()):
            avg_score = round(stats['total_score'] / stats['count'], 1)
            timeline_trends.append({
                'date': date_str,
                'attempts': stats['count'],
                'avg_score': avg_score
            })

        # 5. Leaderboard (Top 10 Students)
        students = get_all_students()
        active_students = [s for s in students if s['attempt_count'] > 0]
        leaderboard = sorted(active_students, key=lambda x: (x['best_percentage'], x['avg_percentage']), reverse=True)[:10]

        # 6. At-Risk Students (Avg score < 60% or latest grade 'Fail'/'D')
        at_risk = [s for s in active_students if s['avg_percentage'] < 60 or s['latest_grade'] in ['Fail', 'D']]

        return {
            'total_attempts': total_attempts,
            'total_students': total_students,
            'total_questions': total_questions,
            'score_distribution': score_bins,
            'grade_distribution': grade_dist,
            'topic_failure_rates': dict(topic_failures),
            'timeline_trends': timeline_trends,
            'leaderboard': leaderboard,
            'at_risk_students': at_risk
        }


def get_database_info():
    """Retrieve database health and storage metrics."""
    with SessionLocal() as session:
        q_count = session.execute(select(func.count()).select_from(Question)).scalar_one()
        u_count = session.execute(select(func.count()).select_from(User)).scalar_one()
        r_count = session.execute(select(func.count()).select_from(AssessmentResult)).scalar_one()

        db_type = engine.dialect.name.upper()

        return {
            'engine': db_type,
            'total_questions': q_count,
            'total_users': u_count,
            'total_results': r_count,
            'status': 'Healthy & Connected',
            'timestamp': datetime.now().isoformat()
        }
