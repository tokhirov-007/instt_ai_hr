import sys
import os
import logging

# Add current dir to path
sys.path.append(os.getcwd())

# Setup logging to see our new logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from app.cv_intelligence.schemas import CVAnalysisResult
from app.candidate_level.schemas import LevelDetectionResult, CandidateLevel
from app.question_engine.question_selector import QuestionSelector

def test_lang_fix():
    print("Testing Multi-Language Fix...")
    
    selector = QuestionSelector()
    
    # Mock LevelDetectionResult
    level_result = LevelDetectionResult(
        candidate_name="Test Candidate",
        level=CandidateLevel.MIDDLE,
        skills=["python", "javascript", "react"],
        confidence_overall=0.9,
        level_score=85.0
    )
    
    languages = ["ru", "en", "uz"]
    
    for lang in languages:
        print(f"\n--- Testing Language: {lang.upper()} ---")
        question_set = selector.select_questions(level_result, max_total_questions=5, lang=lang)
        
        print(f"Total Questions: {question_set.total_questions}")
        for i, q in enumerate(question_set.questions, 1):
            print(f"  {i}. [{q.skill}] {q.question}")
            # Ensure the question text is not in Russian if lang is en or uz
            if lang != "ru":
                russian_markers = ["Что", "Объясните", "Как", "Какие", "Напишите"]
                for marker in russian_markers:
                    if marker in q.question:
                        msg = f"FAIL: Found '{marker}' in [{lang}] question: '{q.question}'"
                        print(msg)
                        assert False, msg
        
        assert question_set.total_questions > 0, f"No questions generated for {lang}!"
    
    print("\n\n=== Validation ===")
    print("[SUCCESS] Multi-language fallback and translation working correctly!")

if __name__ == "__main__":
    test_lang_fix()
