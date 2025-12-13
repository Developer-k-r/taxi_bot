# utils.py - Yordamchi funksiyalar
from config import ADMIN_ID

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def format_order_message(phone_number: str, direction: str, zks: int, latitude: float, longitude: float):
    maps_link = f"[Kartadan koreik ](https://maps.google.com/?q={latitude},{longitude})"
    
    return (
        f"Taza klient 😋:\n"
        f"Telefon 📲: {phone_number}\n"
        f"Yo'nalish 🔁: {direction}\n"
        f"Zakaz soni ✏️: {zks}\n"
        f"Lokatsiya 📍: {maps_link}"
    )