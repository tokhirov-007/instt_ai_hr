from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.bot.schemas import HRAction

def get_candidate_actions_keyboard(session_id: str, candidate_name: str) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for HR to take action on a candidate.
    """
    builder = InlineKeyboardBuilder()
    
    # Callback data format: action:session_id
    builder.row(
        InlineKeyboardButton(
            text="✅ Принять (Invite)", 
            callback_data=f"{HRAction.INVITE.value}:{session_id}"
        ),
        InlineKeyboardButton(
            text="❌ Отклонить (Reject)", 
            callback_data=f"{HRAction.REJECT.value}:{session_id}"
        )
    )
    
    # Second row: Review
    builder.row(
        InlineKeyboardButton(
            text="⏳ Проверить (Review)", 
            callback_data=f"{HRAction.REVIEW.value}:{session_id}"
        )
    )
    
    return builder.as_markup()
