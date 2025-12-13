# keyboards/reply.py - Oddiy tugmalar
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_direction_menu():
   
    kb = [
        [KeyboardButton(text="Shımbayǵa"), KeyboardButton(text="Nókiske")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_location_menu():
    
    kb = [
        [KeyboardButton(text="Lokatsiya jiberiw", request_location=True)],
        [KeyboardButton(text="Biykarlaw")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)