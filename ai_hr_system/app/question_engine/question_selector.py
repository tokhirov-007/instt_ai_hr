from app.question_engine.question_bank import QuestionBank
from app.question_engine.question_generator import QuestionGenerator
from app.question_engine.schemas import Question, QuestionType, DifficultyLevel, QuestionSet
from app.candidate_level.schemas import CandidateLevel, LevelDetectionResult
from app.utils.translator import Translator
from typing import List
import random
import logging

logger = logging.getLogger(__name__)

class QuestionSelector:
    """
    Intelligently selects interview questions based on candidate skills and level.
    """
    
    def __init__(self):
        self.question_bank = QuestionBank()
        self.generator = QuestionGenerator()
        
        # Question distribution by level
        self.level_distribution = {
            CandidateLevel.JUNIOR: {
                "theory_ratio": 0.7,  # 70% theory
                "case_ratio": 0.3,    # 30% case
                "max_questions_per_skill": 1
            },
            CandidateLevel.MIDDLE: {
                "theory_ratio": 0.5,  # 50% theory
                "case_ratio": 0.5,    # 50% case
                "max_questions_per_skill": 1  # Reduced from 2 to 1 for diversity
            },
            CandidateLevel.SENIOR: {
                "theory_ratio": 0.3,  # 30% theory
                "case_ratio": 0.7,    # 70% case
                "max_questions_per_skill": 1  # Reduced from 2 to 1 for diversity
            }
        }
        
        # Difficulty mapping by level
        self.level_difficulty_map = {
            CandidateLevel.JUNIOR: DifficultyLevel.EASY,
            CandidateLevel.MIDDLE: DifficultyLevel.MEDIUM,
            CandidateLevel.SENIOR: DifficultyLevel.HARD
        }
    
    def select_questions(
        self, 
        level_result: LevelDetectionResult,
        max_total_questions: int = 5,
        lang: str = "en"
    ) -> QuestionSet:
        """
        Select interview questions based on candidate level and skills.
        
        Rules:
        - Only select questions for skills the candidate has
        - Respect level-appropriate difficulty
        - Balance theory vs case questions
        - Limit questions per skill
        """
        candidate_level = level_result.level
        # Normalize skills; preserve order but drop empties/duplicates early
        seen_skills = set()
        candidate_skills = []
        for s in (level_result.skills or []):
            if not s:
                continue
            sl = s.lower().strip()
            if not sl or sl in seen_skills:
                continue
            seen_skills.add(sl)
            candidate_skills.append(sl)
        
        distribution = self.level_distribution[candidate_level]
        base_difficulty = self.level_difficulty_map[candidate_level]
        
        selected_questions: List[Question] = []
        
        # Improve relevance/diversity: avoid overlong skill lists and remove ordering bias.
        # Keep a capped set of skills, then shuffle so the same first skills don't always dominate.
        if len(candidate_skills) > 10:
            candidate_skills = candidate_skills[:10]
        random.shuffle(candidate_skills)

        # Select questions for each skill (technical)
        for skill in candidate_skills:
            skill_questions = self._select_questions_for_skill(
                skill=skill,
                difficulty=base_difficulty,
                theory_ratio=distribution["theory_ratio"],
                max_questions=distribution["max_questions_per_skill"],
                lang=lang
            )
            selected_questions.extend(skill_questions)
        
        logger.info(f"[LANG={lang}] skills_detected={len(candidate_skills)} questions_generated={len(selected_questions)}")
        
        # De-duplicate by (skill, text, difficulty, type) to prevent accidental repeats
        deduped = []
        seen = set()
        for q in selected_questions:
            key = (q.skill.lower().strip(), q.question.strip(), str(q.difficulty), str(q.type))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(q)
        selected_questions = deduped

        # Limit total technical questions (after dedupe)
        if len(selected_questions) > max_total_questions:
            selected_questions = random.sample(selected_questions, max_total_questions)
            
        # --- ADDED: Select Soft Skills / Culture Fit Questions ---
        # Select 3 soft skills questions regardless of technical limit
        soft_skills_questions = self._select_questions_for_skill(
            skill="soft_skills",
            difficulty=base_difficulty, # Matches candidate level
            theory_ratio=0.5, # Mix of personality and situational questions
            max_questions=3,
            lang=lang
        )
        # Avoid duplicates between technical and soft-skills lists
        for q in soft_skills_questions:
            key = (q.skill.lower().strip(), q.question.strip(), str(q.difficulty), str(q.type))
            if key in seen:
                continue
            seen.add(key)
            selected_questions.append(q)
        # ---------------------------------------------------------
        
        # Shuffle final list so ordering is less predictable and questions feel more diverse
        random.shuffle(selected_questions)

        logger.info(f"[LANG={lang}] interview_started=true final_questions={len(selected_questions)}")
        
        return QuestionSet(
            candidate_name=level_result.candidate_name,
            candidate_level=str(candidate_level.value),
            questions=selected_questions,
            total_questions=len(selected_questions)
        )
    
    def _select_questions_for_skill(
        self,
        skill: str,
        difficulty: DifficultyLevel,
        theory_ratio: float,
        max_questions: int,
        lang: str = "en"
    ) -> List[Question]:
        """
        Select questions for a specific skill with fallback logic.
        """
        # 1. Try to get available questions for this skill and difficulty in target lang
        available_questions = self.question_bank.get_questions_by_skill_difficulty_lang(
            skill, difficulty, lang
        )
        
        # 2. Fallback to RU if no questions in target lang
        if not available_questions and lang != "ru":
            logger.info(f"[LANG={lang}] No questions for {skill} in bank. Fallback to RU")
            ru_questions = self.question_bank.get_questions_by_skill_difficulty_lang(
                skill, difficulty, "ru"
            )
            if ru_questions:
                # Translate RU questions to target lang
                available_questions = []
                for q in ru_questions:
                    translated_q = q.copy()
                    translated_q.question = Translator.translate(q.question, lang)
                    # Also replace placeholders
                    skill_translated = Translator.translate(skill, lang)
                    translated_q.question = translated_q.question.format(skill=skill_translated.capitalize())
                    translated_q.lang = lang
                    available_questions.append(translated_q)
        
        # 3. Fallback to Generator if still no questions
        if not available_questions:
            logger.info(f"[LANG={lang}] Still no questions for {skill}. Using Generator")
            available_questions = self.generator.generate_questions(
                skill=skill,
                difficulty=difficulty,
                count=max_questions,
                lang=lang
            )
        
        # Separate by type
        theory_questions = [q for q in available_questions if q.type == QuestionType.THEORY]
        case_questions = [q for q in available_questions if q.type == QuestionType.CASE]
        
        selected = []
        
        # Calculate how many of each type to select
        num_theory = int(max_questions * theory_ratio)
        num_case = max_questions - num_theory
        
        # Select theory questions
        if theory_questions and num_theory > 0:
            selected.extend(random.sample(
                theory_questions, 
                min(num_theory, len(theory_questions))
            ))
        
        # Select case questions
        if case_questions and num_case > 0:
            selected.extend(random.sample(
                case_questions,
                min(num_case, len(case_questions))
            ))

        # If we couldn't satisfy the desired count (e.g., no case questions exist),
        # fill from remaining questions to avoid returning fewer questions than requested.
        if len(selected) < max_questions and available_questions:
            remaining = [q for q in available_questions if q not in selected]
            if remaining:
                selected.extend(random.sample(
                    remaining,
                    min(max_questions - len(selected), len(remaining))
                ))
        
        return selected
