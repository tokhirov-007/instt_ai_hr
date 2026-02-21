from typing import List, Dict
from app.scoring.schemas import ScoreBreakdown
from app.scoring.weight_config import get_weights
from app.answer_analysis.schemas import FullIntegrityReport
from app.interview_flow.schemas import SessionSummary
import re

class ScoreEngine:
    """
    Combines technical evaluation, integrity, and behavioral data.
    """

    def _is_non_answer(self, text: str) -> bool:
        """
        Detects if an answer is 'gibberish', 'random text', or 'I don't know' style answers.
        Returns True if the answer should receive 0 points.
        """
        if not text or len(text.strip()) < 2:
            return True
            
        text_lower = text.lower().strip()
        
        # 1. Check for repetitive random characters (e.g., "aaaaa", "asdfgh")
        # Very short repetitive strings or keyboard mashes
        if re.match(r'^(.)\1+$', text_lower): # All same characters like "aaaa"
            return True
            
        # 2. Check for "I don't know" style phrases in RU, UZ, EN
        don_t_know_phrases = [
            # EN
            "don't know", "dont know", "i do not know", "no idea", "not sure", "forgot", "can't remember",
            "random", "idk", "nothing", "none",
            # RU
            "не знаю", "не припомню", "не помню", "без понятия", "забыл", "ничего", "пусто",
            "рандом", "флоп", "аа", "ээ", "хмм", "не могу сказать", "не уверен", "сложно сказать",
            "тд", "т.д.", "и т.д.", "итп", "и т.п.", "хз", "чо", "че", "хх", "йй", "фыва",
            # UZ
            "bilmayman", "eslolmayman", "yodimda yo'q", "tushunmadim", "bilmadim", "unutdim", "t.h", "va h.k", "yo'q"
        ]
        
        for phrase in don_t_know_phrases:
            if phrase in text_lower:
                # If it's a very short answer or contains a strong indicator like 'рандом' or 'не знаю'
                if len(text_lower) < len(phrase) + 15 or phrase in ["рандом", "не знаю", "не помню", "don't know", "bilmayman"]:
                    return True

        # 3. Random gibberish (very low vowel ratio or strange patterns)
        if len(text_lower) > 5:
            vowels_ru = "аеёиоуыэюя"
            vowels_en = "aeiouy" # Added 'y' for keyboard mashes like qwerty
            vowels_uz = "aeiou'o'" 
            vowels = vowels_ru + vowels_en + vowels_uz
            vowel_count = sum(1 for char in text_lower if char in vowels)
            
            # If vowel ratio is extremely low (< 10%)
            if vowel_count / len(text_lower) < 0.1:
                return True
                
            # Keyboard rows
            keyboard_rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "йцукенгшщз", "фывапролдж", "ячсмитьбю"]
            for row in keyboard_rows:
                if row in text_lower or text_lower in row and len(text_lower) > 3:
                    return True

            # Word repetition check (e.g., "blabla blabla blabla")
            words = text_lower.split()
            if len(words) > 3:
                unique_words = set(words)
                if len(unique_words) / len(words) < 0.4: # Over 60% repetition
                    return True
                
        return False

    def calculate_technical_scores(self, summary: SessionSummary, questions: List[Dict]) -> Dict[str, float]:
        """
        Simulate technical scoring by checking for technical keywords 
        and expected topics in answers.
        """
        q_map = {q["id"]: q for q in questions}
        
        technical_scores = []
        problem_solving_scores = []

        for answer in summary.answers:
            q_data = q_map.get(answer.question_id, {})
            expected = q_data.get("expected_topics", [])
            
            # Log zero score reason if no answer or timeout
            if not answer.answer_text or answer.is_timeout:
                print(f"[SCORE_LOG] why_score_zero=True: Question {answer.question_id} has no answer or timeout")
                technical_scores.append(0.0)
                problem_solving_scores.append(0.0)
                continue

            # NEW: CHECK FOR NON-ANSWERS (gibberish/random/I don't know)
            if self._is_non_answer(answer.answer_text):
                print(f"[SCORE_LOG] why_score_zero=True: Non-answer detected for Question {answer.question_id}: '{answer.answer_text}'")
                technical_scores.append(0.0)
                problem_solving_scores.append(0.0)
                continue

            # 1. Knowledge Score: Topic matching
            matches = 0
            for topic in expected:
                if re.search(r'\b' + re.escape(topic.lower()) + r'\b', answer.answer_text.lower()):
                    matches += 1
            
            # Base score from topics
            knowledge_base = (matches / len(expected)) * 100 if expected else 0 # CHANGED: No free 50 pts
            
            # Expanded Technical Keywords (RU/UZ/EN)
            technical_keywords = [
                # EN
                "implementation", "performance", "complexity", "architecture", "pattern", "logic", "database",
                "api", "interface", "class", "object", "function", "method", "async", "sync", "thread",
                "deploy", "ci/cd", "testing", "unit", "integration", "rest", "graphql", "sql", "nosql",
                # RU
                "реализация", "производительность", "сложность", "архитектура", "паттерн", "логика", "база",
                "интерфеис", "класс", "объект", "функция", "метод", "асинхрон", "поток", "деплой",
                "тестирование", "юнит", "интеграция", "рест", "sql", "nosql", "данные", "сервер", "клиент",
                "оптимизация", "кэширование", "безопасность", "авторизация", "аутентификация",
                "пайтон", "питон", "программирование", "разработка", "код", "структура", "алгоритм",
                # UZ
                "amalga oshirish", "unumdorlik", "murakkablik", "arxitektura", "andoza", "mantiq", "ma'lumotlar",
                "interfeys", "sinf", "obyekt", "funktsiya", "usul", "asinxron", "oqim", "joylashtirish",
                "sinash", "birlik", "integratsiya", "rest", "sql", "nosql", "server", "mijoz",
                "optimallashtirish", "keshlash", "xavfsizlik", "tizim", "dastur", "algoritm", "kod"
            ]
            
            # Length Heuristic (Smart Grading)
            word_count = len(answer.answer_text.split())
            length_score = 0
            
            # Count keyword hits early for heuristic usage
            keyword_hits = sum(1 for word in technical_keywords if word in answer.answer_text.lower())
            
            if word_count > 20: 
                if matches > 0 or keyword_hits > 2: # Stricter
                    length_score = 70 
                else:
                    length_score = 0 
            elif word_count > 10:
                if matches > 0 or keyword_hits > 1:
                    length_score = 30 
                else:
                    length_score = 0 
            
            # Keyword Bonus
            keyword_hits = sum(1 for word in technical_keywords if word in answer.answer_text.lower())
            
            # STRICTNESS REFINEMENT: Calculate "Junk Density"
            # If the answer contains keywords BUT is mostly random chars/junk, penalize it.
            # We use \w to include all language characters (RU, UZ, EN).
            junk_chars = re.findall(r'[^\w\s.,?!:;()\-]', answer.answer_text)
            junk_ratio = len(junk_chars) / len(answer.answer_text) if answer.answer_text else 0
            
            # Detect "word mashes" like "python asdfgh" or "js ffff"
            is_keyword_plus_junk = False
            if word_count < 20: # Increased threshold for safety
                # check for gibberish words (long words with extremely low vowel ratio)
                # We include common RU/UZ vowels
                vowels_all = "aeiouyаеёиоуыэюя"
                has_gibberish = any(len(w) > 5 and (sum(1 for c in w.lower() if c in vowels_all) / len(w) < 0.1) for w in answer.answer_text.split())
                
                # If too many very short words (1-2 chars) that aren't common prepositions
                # RU: я, и, в, на, с, а, но, у, к, за
                # UZ: va, bu, u, va, bo'lsa
                common_short = {"я", "и", "в", "на", "с", "а", "но", "у", "к", "за", "от", "до", "по", "об", "va", "bu", "u", "da", "ni", "ni", "ga", "of", "in", "to", "is", "a", "an", "the", "it", "on"}
                very_short_words = [w for w in answer.answer_text.split() if len(w) <= 2 and w.lower() not in common_short]
                
                # REFINED RULE: triggers if high junk ratio OR has gibberish OR too many random short words in a very short answer
                if junk_ratio > 0.4 or has_gibberish or (len(very_short_words) > 3 and word_count < 7):
                    is_keyword_plus_junk = True
            
            if is_keyword_plus_junk:
                print(f"[SCORE_LOG] policy=StrictPenalty: Junk-mixed answer detected for Q{answer.question_id}: '{answer.answer_text}'")
                technical_scores.append(0.0)
                problem_solving_scores.append(0.0)
                continue

            keyword_bonus = min(30, keyword_hits * 5)
            
            # Combine methods: take max of (Topic Match OR Length Heuristic) + Bonus
            knowledge_final = min(100.0, max(knowledge_base, length_score) + keyword_bonus)
            
            if knowledge_final == 0:
                print(f"[SCORE_LOG] why_score_zero=True: Knowledge score 0 for Question {answer.question_id}. Answer: '{answer.answer_text[:50]}...'")
            
            technical_scores.append(knowledge_final)

            # 2. Problem Solving Score (heuristic for case questions)
            is_case = q_data.get("type") == "case"
            if is_case:
                # Better score if they mention "trade-offs", "strategy", "solution"
                ps_markers = [
                    "trade-off", "alternative", "depends", "strategy", "handling", "solution", "scale",
                    "компромисс", "альтернатива", "зависит", "стратегия", "обработка", "решение", "масштабирование",
                    "kelishuv", "muqobil", "bog'liq", "strategiya", "ishlov", "yechim", "miqyoslash",
                    "плюсы", "минусы", "вариант", "лучше", "хуже", "afzallik", "kamchilik"
                ]
                ps_matches = sum(10 for m in ps_markers if m in answer.answer_text.lower())
                # For case studies, length is even more important
                ps_len_score = 75 if word_count > 30 else (50 if word_count > 15 else 0)
                
                ps_score = min(100.0, max(knowledge_base, ps_len_score) + ps_matches)
                
                if ps_score == 0:
                    print(f"[SCORE_LOG] why_score_zero=True: PS score 0 for case question {answer.question_id}")
                problem_solving_scores.append(ps_score)
            else:
                problem_solving_scores.append(knowledge_final * 0.8) # Non-cases don't show full PS

        avg_knowledge = sum(technical_scores) / len(technical_scores) if technical_scores else 0
        avg_ps = sum(problem_solving_scores) / len(problem_solving_scores) if problem_solving_scores else 0
        
        return {
            "knowledge": avg_knowledge,
            "problem_solving": avg_ps
        }

    def calculate_skills_match(self, cv_skills: List[str], questions: List[Dict]) -> float:
        """
        Calculates how well the interview covered the candidate's skills.
        Range: 0-100
        """
        # Fallback: if no CV skills found (parsing error), assume match to avoid penalizing candidate
        if not cv_skills: 
            return 0.0 # CHANGED: No free points if no skills in resume
            
        if not questions:
            return 0.0 # CHANGED: No free points
            
        interview_skills = set()
        for q in questions:
            skill = q.get("skill", "").lower()
            if skill:
                interview_skills.add(skill)
        
        cv_skills_lower = [s.lower() for s in cv_skills]
        matches = 0
        for skill in cv_skills_lower:
            if any(skill in iskill or iskill in skill for iskill in interview_skills):
                matches += 1
                
        return min(100.0, (matches / len(cv_skills_lower)) * 100) if cv_skills_lower else 100.0

    def calculate_confidence_points(self, confidence_level: str) -> float:
        """Maps confidence enum to numerical score (0-100)"""
        mapping = {
            "high": 100.0,
            "medium": 65.0,
            "low": 30.0
        }
        return mapping.get(confidence_level.lower(), 50.0)

    def aggregate(self, 
                  summary: SessionSummary, 
                  integrity_report: FullIntegrityReport,
                  questions: List[Dict],
                  cv_skills: List[str],
                  confidence_level: str) -> ScoreBreakdown:
        """
        Aggregate all data into component scores.
        """
        tech = self.calculate_technical_scores(summary, questions)
        
        # Mapping integrity report results back to components
        honesty = integrity_report.overall_honesty_score * 100
        
        # NEW: Skills Match
        skills_match = self.calculate_skills_match(cv_skills, questions)
        
        # NEW: Confidence Points
        confidence_points = self.calculate_confidence_points(confidence_level)

        return ScoreBreakdown(
            knowledge_score=round(tech["knowledge"], 2),
            honesty_score=round(honesty, 2),
            time_behavior_score=round(skills_match, 2), # Re-using this field for skills_match in SAFE MODE if schema change is restricted
            problem_solving_score=round(confidence_points, 2) # Re-using for confidence_points
        )

    def calculate_final_weighted_score(self, breakdown: ScoreBreakdown, difficulty_mix: str) -> int:
        """
        Calculate score = skills_match + answers_quality + confidence
        Weights: 34% skills_match, 33% technical (answers_quality), 33% confidence
        """
        # In SAFE MODE, we reuse breakdown fields to avoid schema changes if possible
        skills_match = breakdown.time_behavior_score
        answers_quality = breakdown.knowledge_score
        confidence = breakdown.problem_solving_score
        
        # Formula: Each contributes ~33.3 points to max 100
        # CRITICAL: If answers_quality is 0, the overall score should be capped or zeroed.
        if answers_quality < 5:
            return 0
            
        final = (
            (skills_match * 0.34) +
            (answers_quality * 0.33) +
            (confidence * 0.33)
        )
        
        return int(round(final))
