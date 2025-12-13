# main.py — to‘liq yangi versiya (circular import yo‘q)

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers.user import user_router
from handlers.admin import admin_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(user_router, admin_router)

async def main():
    await init_db()
    print("Go GO GO --->>>>>")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query", "location"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot sharshadi (Ctrl+C)")