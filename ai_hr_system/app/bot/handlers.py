from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from app.bot.permissions import BotPermissions
from app.bot.schemas import HRAction
import aiohttp
import logging

import os

logger = logging.getLogger(__name__)

# Configurable backend URL for cross-device support
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

router = Router()
permissions = BotPermissions()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    if not permissions.is_hr(message.from_user.id):
        await message.answer("⛔ <b>Access Denied.</b> This bot is for authorized HR only.", parse_mode="HTML")
        return
    
    await message.answer(
        f"👋 <b>Welcome, HR!</b>\n\n"
        f"ID: <code>{message.from_user.id}</code>\n"
        f"Status: 🟢 Authorized\n\n"
        f"You will receive notifications for all completed interviews here.",
        parse_mode="HTML"
    )

@router.callback_query()
async def process_hr_action(callback: CallbackQuery):
    if not permissions.is_hr(callback.from_user.id):
        await callback.answer("Forbidden", show_alert=True)
        return

    # Callback format: action:session_id
    data = callback.data.split(":")
    if len(data) != 2:
        await callback.answer("Invalid Data")
        return

    action_val, session_id = data
    
    # 1. Map to action status
    status_map = {
        HRAction.INVITE.value: "✅ INVITED",
        HRAction.REJECT.value: "❌ REJECTED",
        HRAction.REVIEW.value: "⏳ UNDER REVIEW"
    }
    
    status_text = status_map.get(action_val, "UNKNOWN")

    # 2. Logic to update backend status via HTTP
    async with aiohttp.ClientSession() as session:
        params = {
            "internal_status": action_val.upper(),
            "hr_id": f"BOT_{callback.from_user.id}"
        }
        
        # We update PUBLIC status ONLY if it's INVITE or REJECT
        if action_val in [HRAction.INVITE.value, HRAction.REJECT.value]:
            params["public_status"] = action_val.upper()

        try:
            url = f"{BACKEND_URL}/update-session-status/{session_id}"
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    logger.info(f"BOT ACTION SUCCESS: HR {callback.from_user.id} updated session {session_id} to {action_val}")
                else:
                    resp_text = await response.text()
                    logger.error(f"BOT ACTION FAILED: Backend returned {response.status}: {resp_text}")
        except Exception as e:
            logger.error(f"BOT ACTION ERROR: Failed to connect to backend: {e}")

    # 3. Update the message to show the decision
    new_text = f"{callback.message.text}\n\n<b>───────────────────</b>\n" \
               f"<b>⚖️ HR DECISION:</b> {status_text}\n" \
               f"👤 <b>By:</b> {callback.from_user.full_name}"
    
    try:
        await callback.message.edit_text(text=new_text, parse_mode="HTML", reply_markup=None)
        await callback.answer(f"Decision saved: {status_text}")
    except Exception as e:
        print(f"Failed to update message: {e}")
        await callback.answer("Decision saved, but UI update failed.")
