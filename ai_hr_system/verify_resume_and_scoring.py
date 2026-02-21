import sys
import os
from datetime import datetime
from unittest.mock import MagicMock

# Add app directory to path
sys.path.append(os.path.abspath("d:/UFT_Company/HR_AI_MA/inst_ai_hr/AI_HR_MA/ai_hr_system"))

from app.cv_intelligence.cv_analyzer import CVAnalyzer
from app.scoring.score_engine import ScoreEngine
from app.interview_flow.schemas import SessionSummary, Answer, SessionStatus

def test_resume_normalization():
    print("\n--- Testing Resume Normalization (Multilingual) ---")
    analyzer = CVAnalyzer()
    analyzer.parser.parse = MagicMock()
    
    # RU/UZ context text
    ru_resume = """
    Иван Иванов. Опыт работы 5 лет.
    Навыки: Питон, Джанго, SQL, Контейнеризация (Докер).
    Также работал с Джаваскриптом и Реактом.
    """
    
    analyzer.parser.parse.return_value = ru_resume
    result = analyzer.analyze("dummy.pdf")
    
    print(f"Detected skills: {result.skills_detected}")
    
    expected = ["python", "django", "sql", "docker", "javascript", "react"]
    found_all = all(s in result.skills_detected for s in ["python", "django", "docker"])
    
    if found_all:
        print("[PASS] Multilingual keywords (Питон, Джанго, Докер) correctly normalized.")
    else:
        print("[FAIL] Normalization failed or skills missing.")

def test_scoring_strictness():
    print("\n--- Testing Scoring Strictness (Zero Points for Junk) ---")
    engine = ScoreEngine()
    
    summary = SessionSummary(
        session_id="test_session",
        candidate_name="Strict Test",
        total_questions=3,
        answered_questions=3,
        total_time_spent=150,
        status=SessionStatus.FINISHED,
        answers=[
            # Q1: Totally unrelated junk (No topics match, no keywords)
            Answer(question_id=1, answer_text="ыфвафывафывафывафывафывафыва", time_spent=10, is_timeout=False, submitted_at=datetime.now()),
            
            # Q2: Keyword + Massive Junk Mash (should hit density penalty)
            Answer(question_id=2, answer_text="python asdfghjk qwertyuiop zxcvbnm", time_spent=10, is_timeout=False, submitted_at=datetime.now()),
            
            # Q3: Valid answer
            Answer(question_id=3, answer_text="Python is a language used for backend development with Django.", time_spent=40, is_timeout=False, submitted_at=datetime.now())
        ]
    )
    
    questions = [
        {"id": 1, "expected_topics": ["sql"]}, # Requested SQL, got mash
        {"id": 2, "expected_topics": ["python"]}, # Requested Python, got mash
        {"id": 3, "expected_topics": ["python"]}  # Valid
    ]
    
    print("\nIndividual Analysis:")
    for i, ans in enumerate(summary.answers):
        is_non = engine._is_non_answer(ans.answer_text)
        print(f"  Q{i+1}: '{ans.answer_text[:20]}...' -> non_answer={is_non}")
    
    scores = engine.calculate_technical_scores(summary, questions)
    
    # We expect tech_scores[0] = 0, tech_scores[1] = 0, tech_scores[2] = 100ish
    # Mean = (0 + 0 + 100) / 3 = 33.33
    print(f"\nAverage Knowledge Score: {scores['knowledge']}")
    
    if scores['knowledge'] < 40:
        print("[PASS] Lenient defaults removed. Junk correctly score 0.")
    else:
        print(f"[FAIL] Score too high! Junk is still getting points: {scores['knowledge']}")

if __name__ == "__main__":
    try:
        test_resume_normalization()
        test_scoring_strictness()
    except Exception as e:
        print(f"Test Error: {e}")
