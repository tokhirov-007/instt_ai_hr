from typing import List
from app.scoring.schemas import RecommendationLevel, ScoreBreakdown

class RecommendationEngine:
    """
    Generates human-readable HR recommendations based on scores and flags.
    """

    def get_recommendation(self, 
                           score: int, 
                           breakdown: ScoreBreakdown, 
                           flags: List[str]) -> tuple[RecommendationLevel, str]:
        """
        Determine recommendation level and descriptive reason.
        """
        
        # 🟢 Decision Matrix
        if score >= 85:
            if breakdown.honesty_score < 60:
                return RecommendationLevel.REVIEW, "Excellent technical knowledge, but significant integrity flags require human verification."
            return RecommendationLevel.STRONG_HIRE, "Exceptional candidate with strong technical depth and authentic communication."
            
        elif score >= 70:
            if breakdown.honesty_score < 50:
                return RecommendationLevel.REVIEW, "Good technical level, but low honesty score suggests potential AI usage or copy-pasting."
            return RecommendationLevel.HIRE, "Solid technical foundation. The candidate displays clear competence in the required skills."
            
        elif score >= 50:
            if "HIGH_RISK_OF_CHEATING" in flags:
                return RecommendationLevel.REJECT, "Candidate showed borderline performance and multiple serious integrity violations."
            return RecommendationLevel.REVIEW, "Average performance. May need additional training or a follow-up interview for clarification."
            
        else:
            reason = "Score is below the required threshold for this position."
            if breakdown.knowledge_score < 40:
                reason = "Insufficient technical knowledge demonstrated during the interview."
            return RecommendationLevel.REJECT, f"Does not meet current requirements. {reason}"

    def generate_comment(self, 
                         level: RecommendationLevel, 
                         breakdown: ScoreBreakdown, 
                         flags: List[str]) -> str:
        """
        Generate a qualitative HR comment (Bilingual RU ||| UZ).
        """
        comments_ru = []
        comments_uz = []
        
        # Technical part
        if breakdown.knowledge_score > 80:
            comments_ru.append("Демонстрирует глубокое понимание концепций.")
            comments_uz.append("Asosiy tushunchalarni chuqur bilishini namoyish etadi.")
        elif breakdown.knowledge_score > 60:
            comments_ru.append("Показывает хорошее понимание стека.")
            comments_uz.append("Texnologiyalar stekini yaxshi tushunadi.")
            
        # Integrity part
        if breakdown.honesty_score < 60:
            comments_ru.append("Заметка: Ответы похожи на AI.")
            comments_uz.append("Eslatma: Javoblar AI ga o'xshaydi.")
        elif breakdown.honesty_score > 90:
            comments_ru.append("Ответы выглядят естественными.")
            comments_uz.append("Javoblar tabiiy va samimiy ko'rinadi.")
            
        # Behavioral part
        if breakdown.time_behavior_score < 50:
            comments_ru.append("Подозрительно быстрые ответы.")
            comments_uz.append("Javoblar shubhali darajada tez berilgan.")
            
        if not comments_ru:
            comments_ru.append("Стандартный результат.")
            comments_uz.append("Standart natija.")
            
        return " ".join(comments_ru) + "|||" + " ".join(comments_uz)
