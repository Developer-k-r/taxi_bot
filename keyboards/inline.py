# keyboards/inline.py - Inline tugmalar
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_confirm(order_id: str):
    kb = [
        [
            InlineKeyboardButton(text="O Aldımǵo", callback_data=f"confirm_{order_id}"),
            InlineKeyboardButton(text="Bl** otkaz", callback_data=f"reject_{order_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)