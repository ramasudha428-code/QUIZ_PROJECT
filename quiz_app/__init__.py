# quiz_app package
"""Package initializer for quiz_app.

Provides convenient imports so other modules can simply do:
    from quiz_app import engine, Base, User, Question, AssessmentResult
"""

# Core database imports (SQLAlchemy engine and models)
from database.session import engine
from database.models import Base, User, Question, AssessmentResult

