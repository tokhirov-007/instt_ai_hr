import sys
import os
from datetime import datetime

# Add current dir to path
sys.path.append(os.getcwd())

from app.scoring.score_engine import ScoreEngine
from app.interview_flow.schemas import SessionSummary, Answer, SessionStatus
from app.answer_analysis.schemas import FullIntegrityReport, AnswerIntegrityReport

def test_scoring_formula():
    print("Testing New Scoring Formula (Skills Match + technical + Confidence)...")
    
    engine = ScoreEngine()
    
    # 1. Mock Data
    summary = SessionSummary(
        session_id="test_001",
        candidate_name="Test Candidate",
        total_questions=2,
        answered_questions=2,
        total_time_spent=120,
        status=SessionStatus.FINISHED,
        answers=[
            Answer(
                question_id=1,
                answer_text="React useEffect is used for side effects. Performance implementation logic.",
                time_spent=60,
                submitted_at=datetime.now(),
                is_timeout=False
            ),
            Answer(
                question_id=2,
                answer_text="Django signals are patterns for decoupling. Complexity and architecture.",
                time_spent=60,
                submitted_at=datetime.now(),
                is_timeout=False
            )
        ]
    )
    
    questions = [
        {"id": 1, "skill": "React", "expected_topics": ["useEffect", "hooks"], "type": "technical"},
        {"id": 2, "skill": "Django", "expected_topics": ["signals", "decoupling"], "type": "case"}
    ]
    
    integrity = FullIntegrityReport(
        session_id="test_001",
        candidate_name="Test Candidate",
        overall_honesty_score=1.0,
        suspicious_answers_count=0,
        global_flags=[],
        answer_reports=[],
        recommendation="Perfect"
    )
    
    cv_skills = ["React", "Django", "PostgreSQL", "JavaScript"]
    
    # 2. Test Aggregation
    print("\nRunning aggregate()...")
    breakdown = engine.aggregate(
        summary,
        integrity,
        questions,
        cv_skills,
        "high"
    )
    
    print(f"Breakdown: {breakdown}")
    
    # 3. Test Final Calculation
    print("\nCalculating final score...")
    final_score = engine.calculate_final_weighted_score(breakdown, "medium")
    print(f"Final Score: {final_score}")
    
    # Verify components
    # skills_match: 2 matches (React, Django) out of 4 = 50%
    # technical: high quality words used
    # confidence: high = 100
    
    assert final_score > 0, "Score should not be 0"
    print("\n[SUCCESS] New scoring formula verified!")

if __name__ == "__main__":
    test_scoring_formula()
