from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    cv_path = Column(String)
    language = Column(String, default="en")
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("SessionModel", back_populates="candidate")

class SessionModel(Base):
    __tablename__ = "interview_sessions"

    id = Column(String, primary_key=True, index=True) # session_id (UUID)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    
    # Snapshot of candidate details at the time of session
    candidate_name = Column(String, nullable=True)
    candidate_phone = Column(String, nullable=True)
    candidate_email = Column(String, nullable=True)
    candidate_lang = Column(String, default="en")  # Language used in this session
    
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    status = Column(String) # active, finished, etc.
    status_internal = Column(String, default="PENDING")
    status_public = Column(String, default="UNDER_REVIEW")
    
    total_questions = Column(Integer)
    current_question_index = Column(Integer, default=0)
    
    questions = Column(JSON) # List of dicts
    answers = Column(JSON)   # List of dicts
    
    # Analysis results
    ai_summary = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    hr_comment = Column(Text, nullable=True)
    decision = Column(String, nullable=True)
    confidence = Column(String, nullable=True)
    flags = Column(JSON, nullable=True)  # List of flags from AI analysis
    
    candidate = relationship("Candidate", back_populates="sessions")
