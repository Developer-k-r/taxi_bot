# states.py - FSM state'lar
from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    phone_number = State()  # Raqam kiritish

class ChangePhoneState(StatesGroup):
    new_phone = State()  # Yangi raqam kiritish

class DirectionState(StatesGroup):
    choose = State()  # Yo'nalish tanlash

class LocationState(StatesGroup):
    send = State()  # Lokatsiya yuborish
# states.py — yangi state qo‘shing

class AdminStates(StatesGroup):
    waiting_for_ads_text = State()  # Reklama matnini kutish