import sys
import os
from datetime import datetime
from unittest.mock import MagicMock

# Add app directory to path
sys.path.append(os.path.abspath("d:/UFT_Company/HR_AI_MA/inst_ai_hr/AI_HR_MA/ai_hr_system"))

from app.scoring.score_engine import ScoreEngine
from app.interview_flow.schemas import SessionSummary, Answer, SessionStatus

def test_non_answers():
    engine = ScoreEngine()
    
    test_cases = [
        ("aa", True),
        ("aaaaaaa", True),
        ("не знаю", True),
        ("don't know", True),
        ("bilmayman", True),
        ("sdfghjkl", True), # Gibberish (no vowels)
        ("qwertyuiop", True), # Keyboard row
        ("I actually have a lot of experience with React", False), # Valid
        ("Я не знаю как это сделать, но могу попробовать", True), # Triggered by 'не знаю'
        ("просто рандом какой-то", True),
        ("не помню", True),
        ("random stuff", True),
    ]
    
    print("\n--- Verifying _is_non_answer logic ---")
    all_pass = True
    for text, expected in test_cases:
        result = engine._is_non_answer(text)
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL": all_pass = False
        print(f"[{status}] Text: '{text}' | Expected Non-Answer: {expected} | Actual: {result}")

    # Verify calculate_technical_scores returns 0 for these
    summary = SessionSummary(
        session_id="test_session",
        candidate_name="Test User",
        total_questions=3,
        answered_questions=3,
        total_time_spent=60,
        status=SessionStatus.FINISHED,
        answers=[
            Answer(question_id=1, answer_text="aaaa", time_spent=5, is_timeout=False, submitted_at=datetime.now()),
            Answer(question_id=2, answer_text="не знаю", time_spent=5, is_timeout=False, submitted_at=datetime.now()),
            Answer(question_id=3, answer_text="Python is a programming language", time_spent=30, is_timeout=False, submitted_at=datetime.now())
        ]
    )
    
    questions = [
        {"id": 1, "expected_topics": ["python"]},
        {"id": 2, "expected_topics": ["sql"]},
        {"id": 3, "expected_topics": ["python"]}
    ]
    
    scores = engine.calculate_technical_scores(summary, questions)
    print("\n--- Verifying Technical Scores ---")
    print(f"Knowledge Score: {scores['knowledge']}")
    
    # q1=0, q2=0, q3=Topic match(100)
    # Total = (0+0+100)/3 = 33.33
    if 30 < scores['knowledge'] < 40:
        print("[PASS] Scoring logic correctly penalized non-answers.")
    else:
        print(f"[FAIL] Scoring logic result unexpected: {scores['knowledge']}")
        all_pass = False

    if all_pass:
        print("\n[SUCCESS] All tests passed!")
        sys.exit(0)
    else:
        print("\n[FAILURE] Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    test_non_answers()
