from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    assessment_results = relationship("AssessmentResult", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # Store JSON array as string
    answer = Column(String, nullable=False)
    topic = Column(String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "options": json.loads(self.options),
            "answer": self.answer,
            "topic": self.topic,
        }

class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    grade = Column(String, nullable=False)
    weak_topics = Column(Text, nullable=False)
    feedback = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="assessment_results")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "score": self.score,
            "percentage": self.percentage,
            "grade": self.grade,
            "weak_topics": json.loads(self.weak_topics),
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
