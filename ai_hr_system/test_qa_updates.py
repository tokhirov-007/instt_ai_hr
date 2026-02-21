
import sys
import os
import asyncio
from app.candidate_level.schemas import LevelDetectionResult, CandidateLevel
from app.question_engine.question_selector import QuestionSelector

# Mock app context
sys.path.append(os.getcwd())

async def test_question_generation():
    print("Testing Question Generation with Soft Skills...")
    selector = QuestionSelector()
    
    # Mock Level Result
    level_result = LevelDetectionResult(
        candidate_name="Test Candidate",
        level=CandidateLevel.MIDDLE,
        skills=["Python", "Django"],
        reasoning="Test",
        confidence_overall=0.85
    )
    
    # Generate Questions
    # Request 3 technical questions
    q_set = selector.select_questions(level_result, max_total_questions=3, lang="ru")
    
    print(f"Total Questions Generated: {len(q_set.questions)}")
    for i, q in enumerate(q_set.questions):
        print(f"{i+1}. [{q.skill}] ({q.difficulty}) {q.question}")
        
    # Check if soft skills are present
    soft_skills = [q for q in q_set.questions if q.skill == "soft_skills"]
    if len(soft_skills) >= 1:
        print("\n✅ Soft Skills questions found!")
    else:
        print("\n❌ Soft Skills questions NOT found!")

if __name__ == "__main__":
    asyncio.run(test_question_generation())
