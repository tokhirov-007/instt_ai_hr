
from app.question_engine.question_bank import QuestionBank
from app.question_engine.schemas import DifficultyLevel

bank = QuestionBank()
print("Bank Initialized.")
print(f"Total Questions: {len(bank.questions)}")

skill = "soft_skills"
difficulty = DifficultyLevel.MEDIUM
lang = "ru"

questions = bank.get_questions_by_skill_difficulty_lang(skill, difficulty, lang)
print(f"Questions for {skill} ({difficulty}, {lang}): {len(questions)}")

for q in questions:
    print(f"- {q.question}")

# Check all soft skills questions
all_soft = bank.get_questions_by_skill(skill)
print(f"\nAll Soft Skills questions ({len(all_soft)}):")
for q in all_soft:
    print(f"- [{q.difficulty}] [{q.lang}] {q.question}")
