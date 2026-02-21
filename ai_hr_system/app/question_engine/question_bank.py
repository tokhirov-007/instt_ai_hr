from app.question_engine.schemas import Question, QuestionType, DifficultyLevel
from typing import List, Dict

class QuestionBank:
    """
    Structured question database organized by skill, difficulty, and type.
    """
    
    def __init__(self):
        self.questions: List[Question] = self._initialize_questions()
        self._build_indexes()
    
    def _initialize_questions(self) -> List[Question]:
        """Initialize the question bank with pre-defined questions"""
        questions = []
        
        # Python Questions
        questions.extend([
            Question(
                id=1, skill="python", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Что такое list comprehension в Python и когда его использовать?",
                expected_topics=["list comprehension", "syntax", "performance"],
                lang="ru"
            ),
            Question(
                id=1001, skill="python", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="What is list comprehension in Python?",
                expected_topics=["list comprehension", "syntax", "performance"],
                lang="en"
            ),
            Question(
                id=2, skill="python", difficulty=DifficultyLevel.EASY, type=QuestionType.CASE,
                question="Напишите функцию, которая находит все уникальные элементы в списке.",
                expected_topics=["set", "list", "uniqueness"],
                lang="ru"
            ),
            Question(
                id=3, skill="python", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.THEORY,
                question="Объясните разницу между @staticmethod и @classmethod.",
                expected_topics=["decorators", "methods", "OOP"],
                lang="ru"
            ),
            Question(
                id=4, skill="python", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Как бы вы оптимизировали код, который обрабатывает большой CSV файл?",
                expected_topics=["generators", "memory", "performance"],
                lang="ru"
            ),
            Question(
                id=5, skill="python", difficulty=DifficultyLevel.HARD, type=QuestionType.THEORY,
                question="Объясните работу GIL (Global Interpreter Lock) и его влияние на многопоточность.",
                expected_topics=["GIL", "threading", "concurrency"],
                lang="ru"
            ),
            Question(
                id=6, skill="python", difficulty=DifficultyLevel.HARD, type=QuestionType.CASE,
                question="Спроектируйте систему кэширования с TTL для API запросов.",
                expected_topics=["caching", "TTL", "design patterns"],
                lang="ru"
            ),
        ])
        
        # JavaScript Questions
        questions.extend([
            Question(
                id=7, skill="javascript", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Что такое замыкание (closure) в JavaScript?",
                expected_topics=["closure", "scope", "functions"],
                lang="ru"
            ),
            Question(
                id=8, skill="javascript", difficulty=DifficultyLevel.EASY, type=QuestionType.CASE,
                question="Напишите функцию debounce для оптимизации поиска.",
                expected_topics=["debounce", "setTimeout", "optimization"],
                lang="ru"
            ),
            Question(
                id=9, skill="javascript", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.THEORY,
                question="Объясните разницу между Promise и async/await.",
                expected_topics=["promises", "async", "asynchronous"],
                lang="ru"
            ),
            Question(
                id=10, skill="javascript", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Как бы вы оптимизировали работу асинхронных запросов в SPA?",
                expected_topics=["async", "promises", "performance"],
                lang="ru"
            ),
            Question(
                id=11, skill="javascript", difficulty=DifficultyLevel.HARD, type=QuestionType.THEORY,
                question="Объясните Event Loop и как работает очередь микрозадач.",
                expected_topics=["event loop", "microtasks", "macrotasks"],
                lang="ru"
            ),
            Question(
                id=12, skill="javascript", difficulty=DifficultyLevel.HARD, type=QuestionType.CASE,
                question="Спроектируйте систему управления состоянием для большого приложения.",
                expected_topics=["state management", "architecture", "patterns"],
                lang="ru"
            ),
        ])
        
        # React Questions
        questions.extend([
            Question(
                id=13, skill="react", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Что такое Virtual DOM и зачем он нужен?",
                expected_topics=["virtual DOM", "reconciliation", "performance"],
                lang="ru"
            ),
            Question(
                id=14, skill="react", difficulty=DifficultyLevel.EASY, type=QuestionType.CASE,
                question="Создайте простой компонент счётчика с useState.",
                expected_topics=["useState", "hooks", "state"],
                lang="ru"
            ),
            Question(
                id=15, skill="react", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.THEORY,
                question="Объясните useEffect и его зависимости.",
                expected_topics=["useEffect", "lifecycle", "dependencies"],
                lang="ru"
            ),
            Question(
                id=16, skill="react", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Как избежать лишних ререндеров в React?",
                expected_topics=["memo", "useMemo", "useCallback", "optimization"],
                lang="ru"
            ),
            Question(
                id=17, skill="react", difficulty=DifficultyLevel.HARD, type=QuestionType.THEORY,
                question="Объясните работу React Fiber и приоритизацию рендеринга.",
                expected_topics=["fiber", "concurrent mode", "scheduling"],
                lang="ru"
            ),
            Question(
                id=18, skill="react", difficulty=DifficultyLevel.HARD, type=QuestionType.CASE,
                question="Спроектируйте архитектуру для микрофронтенд приложения на React.",
                expected_topics=["microfrontends", "architecture", "module federation"],
                lang="ru"
            ),
        ])
        
        # Node.js Questions
        questions.extend([
            Question(
                id=19, skill="node.js", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Что такое middleware в Express.js?",
                expected_topics=["middleware", "express", "request pipeline"],
                lang="ru"
            ),
            Question(
                id=20, skill="node.js", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Как организовать обработку ошибок в Express приложении?",
                expected_topics=["error handling", "middleware", "try-catch"],
                lang="ru"
            ),
            Question(
                id=21, skill="node.js", difficulty=DifficultyLevel.HARD, type=QuestionType.CASE,
                question="Спроектируйте систему обработки очередей с использованием Node.js.",
                expected_topics=["queues", "workers", "scalability"],
                lang="ru"
            ),
        ])
        
        # Django Questions
        questions.extend([
            Question(
                id=22, skill="django", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Что такое ORM в Django и как он работает?",
                expected_topics=["ORM", "models", "database"],
                lang="ru"
            ),
            Question(
                id=23, skill="django", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Как оптимизировать запросы к базе данных в Django?",
                expected_topics=["select_related", "prefetch_related", "N+1 problem"],
                lang="ru"
            ),
            Question(
                id=24, skill="django", difficulty=DifficultyLevel.HARD, type=QuestionType.CASE,
                question="Спроектируйте систему прав доступа для многопользовательского приложения.",
                expected_topics=["permissions", "authentication", "authorization"],
                lang="ru"
            ),
        ])
        
        # Database Questions
        questions.extend([
            Question(
                id=25, skill="postgresql", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Что такое индексы и зачем они нужны?",
                expected_topics=["indexes", "performance", "queries"],
                lang="ru"
            ),
            Question(
                id=26, skill="postgresql", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Как бы вы оптимизировали медленный SQL запрос?",
                expected_topics=["EXPLAIN", "indexes", "query optimization"],
                lang="ru"
            ),
            Question(
                id=27, skill="sql", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Объясните разницу между INNER JOIN и LEFT JOIN.",
                expected_topics=["joins", "SQL", "relationships"],
                lang="ru"
            ),
        ])
        
        # Docker Questions
        questions.extend([
            Question(
                id=28, skill="docker", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Что такое Docker контейнер и чем он отличается от виртуальной машины?",
                expected_topics=["containers", "virtualization", "isolation"],
                lang="ru"
            ),
            Question(
                id=29, skill="docker", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Как организовать multi-stage build для оптимизации Docker образа?",
                expected_topics=["multi-stage", "optimization", "Dockerfile"],
                lang="ru"
            ),
            Question(
                id=30, skill="docker", difficulty=DifficultyLevel.HARD, type=QuestionType.CASE,
                question="Спроектируйте Docker Compose конфигурацию для микросервисной архитектуры.",
                expected_topics=["docker-compose", "microservices", "networking"],
                lang="ru"
            ),
        ])

        # Soft Skills & Culture Fit Questions (Added per user request)
        questions.extend([
            Question(
                id=101, skill="soft_skills", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Как вы относитесь к работе в коллективе? Что для вас важнее: личный результат или успех команды?",
                expected_topics=["teamwork", "collaboration", "communication"],
                lang="ru"
            ),
            Question(
                id=102, skill="soft_skills", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Как бы вы описали свой тип личности: интроверт, экстраверт или амбиверт? Как это влияет на вашу работу?",
                expected_topics=["personality", "self-awareness", "work style"],
                lang="ru"
            ),
            Question(
                id=103, skill="soft_skills", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Представьте, что у вас возник конфликт с коллегой по поводу технического решения. Ваши действия?",
                expected_topics=["conflict resolution", "professionalism", "compromise"],
                lang="ru"
            ),
            Question(
                id=104, skill="soft_skills", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.THEORY,
                question="Что вас больше всего мотивирует в работе, кроме финансовой составляющей?",
                expected_topics=["motivation", "growth", "values"],
                lang="ru"
            ),
            Question(
                id=105, skill="soft_skills", difficulty=DifficultyLevel.HARD, type=QuestionType.CASE,
                question="Вам нужно сообщить руководителю о том, что вы не успеваете сдать проект в срок. Как вы это сделаете?",
                expected_topics=["transparency", "responsibility", "planning"],
                lang="ru"
            ),
            Question(
                id=106, skill="soft_skills", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Опишите идеальную для вас рабочую атмосферу и культуру компании.",
                expected_topics=["culture fit", "environment", "values"],
                lang="ru"
            ),
            Question(
                id=107, skill="soft_skills", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Что для вас важно при выборе компании: продукт, команда, уровень зарплаты, возможности роста? Расставьте по приоритету.",
                expected_topics=["company choice", "values", "growth"],
                lang="ru"
            ),
            Question(
                id=108, skill="soft_skills", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Представьте, что ценности компании частично расходятся с вашими личными. Как вы будете действовать в такой ситуации?",
                expected_topics=["company values", "conflict of values", "ethics"],
                lang="ru"
            ),
            Question(
                id=109, skill="soft_skills", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.THEORY,
                question="Какой стиль управления (микроменеджмент, доверие, гибкость) для вас наиболее комфортен и почему?",
                expected_topics=["management style", "expectations", "communication"],
                lang="ru"
            ),
            Question(
                id=110, skill="soft_skills", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Компания переживает период активных изменений (рост, смена приоритетов). Как вы обычно адаптируетесь к таким ситуациям?",
                expected_topics=["change management", "adaptability", "company growth"],
                lang="ru"
            ),
            Question(
                id=111, skill="soft_skills", difficulty=DifficultyLevel.HARD, type=QuestionType.CASE,
                question="Опишите ситуацию, когда вы были не согласны с решением руководства. Как вы выстроили диалог и к чему это привело?",
                expected_topics=["communication with management", "disagreement", "conflict resolution"],
                lang="ru"
            ),
            Question(
                id=112, skill="soft_skills", difficulty=DifficultyLevel.HARD, type=QuestionType.THEORY,
                question="Как вы понимаете 'здоровую корпоративную культуру'? Какие сигналы для вас говорят о том, что в компании с этим есть проблемы?",
                expected_topics=["corporate culture", "company health", "red flags"],
                lang="ru"
            ),
            Question(
                id=113, skill="soft_skills", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.THEORY,
                question="Как вы относитесь к удалённому формату работы по сравнению с офисным? В чём плюсы и минусы для вас лично?",
                expected_topics=["remote work", "office", "productivity"],
                lang="ru"
            ),
            Question(
                id=114, skill="soft_skills", difficulty=DifficultyLevel.EASY, type=QuestionType.THEORY,
                question="Что помогает вам сохранять мотивацию и вовлечённость в долгосрочных проектах компании?",
                expected_topics=["motivation", "long-term projects", "engagement"],
                lang="ru"
            ),
            Question(
                id=115, skill="soft_skills", difficulty=DifficultyLevel.MEDIUM, type=QuestionType.CASE,
                question="Представьте, что вам не до конца понятна стратегия компании. Какие шаги вы предпримете, чтобы лучше её понять?",
                expected_topics=["strategy", "questions", "initiative"],
                lang="ru"
            ),
        ])
        
        return questions
    
    def _build_indexes(self):
        """Build indexes for fast lookup"""
        self.by_skill: Dict[str, List[Question]] = {}
        self.by_difficulty: Dict[DifficultyLevel, List[Question]] = {}
        self.by_type: Dict[QuestionType, List[Question]] = {}
        
        for question in self.questions:
            # Index by skill
            skill_lower = question.skill.lower()
            if skill_lower not in self.by_skill:
                self.by_skill[skill_lower] = []
            self.by_skill[skill_lower].append(question)
            
            # Index by difficulty
            if question.difficulty not in self.by_difficulty:
                self.by_difficulty[question.difficulty] = []
            self.by_difficulty[question.difficulty].append(question)
            
            # Index by type
            if question.type not in self.by_type:
                self.by_type[question.type] = []
            self.by_type[question.type].append(question)
    
    def get_questions_by_skill(self, skill: str) -> List[Question]:
        """Get all questions for a specific skill"""
        return self.by_skill.get(skill.lower(), [])
    
    def get_questions_by_skill_difficulty_lang(
        self, 
        skill: str, 
        difficulty: DifficultyLevel,
        lang: str = "en"
    ) -> List[Question]:
        """Get questions filtered by skill, difficulty and language"""
        skill_questions = self.get_questions_by_skill(skill)
        return [q for q in skill_questions if q.difficulty == difficulty and q.lang == lang]
