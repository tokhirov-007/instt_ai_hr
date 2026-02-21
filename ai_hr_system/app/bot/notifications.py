from aiogram import Bot
from app.bot.keyboards import get_candidate_actions_keyboard
from app.scoring.schemas import FinalRecommendation
from app.bot.permissions import BotPermissions

class BotNotificationManager:
    """
    Handles formatting and sending notifications to HR.
    """
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.permissions = BotPermissions()

    async def notify_new_candidate(self, recommendation: FinalRecommendation):
        """
        Sends a rich HTML notification to all authorized HR IDs.
        """
        hr_ids = self.permissions.get_hr_ids()
        if not hr_ids:
            print("ERROR: No HR IDs configured. Notification not sent.")
            return

        message_html = self._format_hr_report(recommendation)
        
        keyboard = get_candidate_actions_keyboard(
            session_id=recommendation.session_id,
            candidate_name=recommendation.candidate_name
        )

        for hr_id in hr_ids:
            try:
                await self.bot.send_message(
                    chat_id=hr_id,
                    text=message_html,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Failed to send notification to HR {hr_id}: {e}")

    def _format_hr_report(self, rec: FinalRecommendation) -> str:
        """Formats the bilingual HTML report for Telegram with RU/UZ separation."""
        
        # MAPPINGS
        DECISIONS_RU = {
            "Strong Hire": "Настоятельно рекомендую",
            "Hire": "Нанять",
            "Review": "На проверку",
            "Reject": "Отказать"
        }
        DECISIONS_UZ = {
            "Strong Hire": "Juda tavsiya etiladi",
            "Hire": "Ishga olish",
            "Review": "Ko'rib chiqish",
            "Reject": "Rad etish"
        }
        
        FLAGS_MAP = {
            # AI Detector Flags
            "superhuman_typing_speed": ("Нереальная скорость печати", "G'ayritabiiy yozish tezligi"),
            "fast_typing_suspicion": ("Подозрительно быстрая печать", "Shubhali tez yozish"),
            "perfect_numbered_list": ("Идеальные списки (AI)", "Mukammal ro'yxatlar (AI)"),
            "perfect_bullet_points": ("Идеальные пункты (AI)", "Mukammal punktlar (AI)"),
            "uniform_sentence_lengths": ("Монотонные предложения", "Bir xil gap uzunligi"),
            "high_marker_density": ("Много AI-фраз", "Ko'p AI iboralari"),
            "empty_text": ("Пустой ответ", "Bo'sh javob"),
            "ai_star_formatting": ("Форматирование через звездочки (*)", "Yulduzchali formatlash (*)"),
            "colon_definitions_pattern": ("Стиль 'Термин: Определение'", "'Termin: Ta'rif' uslubi"),
            "high_repetition_rate": ("Высокая повторяемость слов", "So'zlar qaytarilishi yuqori"),
            "robot_transitions": ("Роботизированные связки", "Robotga xos bog'lamlar"),
            
            # Structure Analyzer Flags
            "contains_code": ("Содержит код", "Kod mavjud"),
            "logical_steps_detected": ("Логические шаги обнаружены", "Mantiqiy qadamlar aniqlandi"),
            "lack_of_explaining_steps": ("Отсутствие объяснений", "Tushuntirishlar yo'q"),
            "comprehensive_answer": ("Полный ответ", "To'liq javob"),
            "too_short_answer": ("Слишком короткий ответ", "Juda qisqa javob"),
            "raw_code_no_explanation": ("Код без объяснений", "Tushuntirishsiz kod"),
            "long_text_no_code": ("Длинный текст без кода", "Kodsiz uzun matn"),
            
            # Time Behavior Flags
            "too_fast_for_hard_question": ("Слишком быстро для сложного вопроса", "Qiyin savol uchun juda tez"),
            "too_fast_for_medium_question": ("Слишком быстро для среднего вопроса", "O'rta savol uchun juda tez"),
            "suspiciously_short_time": ("Подозрительно короткое время", "Shubhali qisqa vaqt"),
            "impossible_typing_speed": ("Невозможная скорость печати", "Imkonsiz yozish tezligi"),
            "extremely_high_typing_speed": ("Экстремально высокая скорость", "Haddan tashqari yuqori tezlik"),
            
            # Plagiarism Checker Flags
            "known_template_detected": ("Обнаружен известный шаблон", "Ma'lum shablon aniqlandi"),
            "possible_templated_phrasing": ("Возможно шаблонные фразы", "Shablon iboralar bo'lishi mumkin"),
            "high_self_similarity": ("Высокое самоповторение", "Yuqori o'z-o'zini takrorlash"),
            
            # Final Analyzer Global Flags
            "HIGH_RISK_OF_CHEATING": ("ВЫСОКИЙ РИСК ОБМАНА", "ALDASH XAVFI YUQORI"),
            "SYSTEMIC_AI_USAGE_LIKELY": ("СИСТЕМНОЕ ИСПОЛЬЗОВАНИЕ AI", "Tizimli AI foydalanish")
        }

        # Color Indicators (emojis)
        score_emoji = "🟢" if rec.final_score >= 70 else "🟡" if rec.final_score >= 50 else "🔴"
        
        # Split Comments (RU ||| UZ)
        comment_parts = rec.hr_comment.split("|||")
        comment_ru = comment_parts[0].strip()
        comment_uz = comment_parts[1].strip() if len(comment_parts) > 1 else comment_parts[0].strip()

        # Translate Decision
        decision_ru = DECISIONS_RU.get(rec.decision, rec.decision)
        decision_uz = DECISIONS_UZ.get(rec.decision, rec.decision)

        # Format Reasons (Localized)
        reasons_ru_list = []
        reasons_uz_list = []
        
        for f in rec.flags[:3]:
            # Try to find mapping, else use raw
            if f in FLAGS_MAP:
                reasons_ru_list.append(f"• {FLAGS_MAP[f][0]}")
                reasons_uz_list.append(f"• {FLAGS_MAP[f][1]}")
            else:
                reasons_ru_list.append(f"• {f}")
                reasons_uz_list.append(f"• {f}")
        
        reasons_ru_str = "\n".join(reasons_ru_list) if reasons_ru_list else "• (Нет замечаний)"
        reasons_uz_str = "\n".join(reasons_uz_list) if reasons_uz_list else "• (Izohlar yo'q)"

        # Russian block
        ru_header = f"🇷🇺 <b>НОВЫЙ КАНДИДАТ</b>\n"
        ru_details = (
            f"👤 <b>Кандидат:</b> {rec.candidate_name}\n"
            f"🆔 <b>Сессия:</b> <code>{rec.session_id}</code>\n"
            f"────────────────\n"
            f"{score_emoji} <b>Балл:</b> {rec.final_score}/100\n"
            f"────────────────\n"
            f"<b>📊 Решение:</b> <i>{decision_ru}</i>\n"
            f"<b>💬 Комментарий:</b> {comment_ru}\n"
            f"<b>🚨 Причины:</b>\n{reasons_ru_str}\n"
        )

        # Uzbek block
        uz_header = f"🇺🇿 <b>YANGI NOMZOD</b>\n"
        uz_details = (
            f"👤 <b>Nomzod:</b> {rec.candidate_name}\n"
            f"🆔 <b>Sessiya:</b> <code>{rec.session_id}</code>\n"
            f"────────────────\n"
            f"{score_emoji} <b>Ball:</b> {rec.final_score}/100\n"
            f"────────────────\n"
            f"<b>📊 Bashorat:</b> <i>{decision_uz}</i>\n"
            f"<b>💬 Izoh:</b> {comment_uz}\n"
            f"<b>🚨 Sabablar:</b>\n{reasons_uz_str}\n"
        )

        return (
            f"{ru_header}\n{ru_details}\n"
            f"<b>---------------------</b>\n\n"
            f"{uz_header}\n{uz_details}"
        )
