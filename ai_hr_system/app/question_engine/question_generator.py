from app.question_engine.schemas import Question, QuestionType, DifficultyLevel
from typing import List

class QuestionGenerator:
    """
    AI-based question generator for fallback when question bank doesn't have suitable questions.
    Uses template-based generation (no external LLM required).
    """
    
    def __init__(self):
        # Question templates by difficulty and type
        self.templates = {
            DifficultyLevel.EASY: {
                QuestionType.THEORY: [
                    "Что такое {skill} и для чего он используется?",
                    "Объясните основные концепции {skill}.",
                    "Какие преимущества даёт использование {skill}?"
                ],
                QuestionType.CASE: [
                    "Напишите простой пример использования {skill}.",
                    "Как бы вы решили базовую задачу с помощью {skill}?",
                    "Создайте простое приложение используя {skill}."
                ]
            },
            DifficultyLevel.MEDIUM: {
                QuestionType.THEORY: [
                    "Объясните продвинутые возможности {skill}.",
                    "Какие best practices существуют для {skill}?",
                    "Сравните {skill} с альтернативными решениями."
                ],
                QuestionType.CASE: [
                    "Как бы вы оптимизировали производительность в {skill}?",
                    "Спроектируйте решение для типичной задачи с {skill}.",
                    "Как обработать ошибки при работе с {skill}?"
                ]
            },
            DifficultyLevel.HARD: {
                QuestionType.THEORY: [
                    "Объясните внутреннее устройство {skill}.",
                    "Какие архитектурные паттерны применимы для {skill}?",
                    "Как {skill} работает под капотом?"
                ],
                QuestionType.CASE: [
                    "Спроектируйте масштабируемую систему используя {skill}.",
                    "Как бы вы решили сложную архитектурную задачу с {skill}?",
                    "Оптимизируйте высоконагруженное приложение на {skill}."
                ]
            }
        }
        
        self.next_id = 1000  # Start generated questions from ID 1000
    
    def generate_question(
        self,
        skill: str,
        difficulty: DifficultyLevel,
        question_type: QuestionType,
        lang: str = "ru"
    ) -> Question:
        """
        Generate a question for a specific skill, difficulty, and type.
        """
        from app.utils.translator import Translator
        
        # Get templates for this difficulty and type
        templates = self.templates[difficulty][question_type]
        
        # Select a random template
        import random
        template_ru = random.choice(templates)
        
        # Translate template
        template = Translator.translate(template_ru, lang)
        
        # Format with skill name
        skill_translated = Translator.translate(skill, lang)
        question_text = template.format(skill=skill_translated.capitalize())
        
        # Generate expected topics based on skill
        expected_topics_ru = self._generate_expected_topics(skill, difficulty)
        expected_topics = [Translator.translate(t, lang) for t in expected_topics_ru]
        
        # Create question
        question = Question(
            id=self.next_id,
            skill=skill,
            difficulty=difficulty,
            type=question_type,
            question=question_text,
            lang=lang,
            expected_topics=expected_topics
        )
        
        self.next_id += 1
        return question
    
    def generate_questions(
        self,
        skill: str,
        difficulty: DifficultyLevel,
        count: int = 1,  # Reduced from 2 to 1 for diversity
        lang: str = "ru"
    ) -> List[Question]:
        """
        Generate multiple questions for a skill.
        """
        questions = []
        
        # Generate mix of theory and case
        num_theory = count // 2
        num_case = count - num_theory
        
        for _ in range(num_theory):
            questions.append(
                self.generate_question(skill, difficulty, QuestionType.THEORY, lang=lang)
            )
        
        for _ in range(num_case):
            questions.append(
                self.generate_question(skill, difficulty, QuestionType.CASE, lang=lang)
            )
        
        return questions
    
    def _generate_expected_topics(
        self,
        skill: str,
        difficulty: DifficultyLevel
    ) -> List[str]:
        """
        Generate expected topics based on skill and difficulty.
        """
        base_topics = [skill, "best practices"]
        
        if difficulty == DifficultyLevel.EASY:
            base_topics.extend(["basics", "syntax"])
        elif difficulty == DifficultyLevel.MEDIUM:
            base_topics.extend(["optimization", "patterns"])
        else:  # HARD
            base_topics.extend(["architecture", "scalability", "performance"])
        
        return base_topics
