from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import aiosqlite

from config import ADMIN_ID, DB_NAME
from database import get_user_count, get_all_users, export_data, get_zks
from states import AdminStates
from utils import is_admin

admin_router = Router()



def admin_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id != ADMIN_ID:
            return  
        return await func(message, *args, **kwargs)
    return wrapper

@admin_router.message(Command("start"))
async def admin_start(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Salem, brat! Tómendegi buyrıqlar bar:\n"
                        "/members - paydalanıwshılar sanı\n"
                        "/stats - Ulıwma statistika\n"
                        "/ads - Hámmege reklama jiberiw (reply etip jazıń) \n"
                        "/data - Magliwmatlar bazasın alıw")
@admin_router.message(Command("members"))
async def cmd_members(message: Message):
    if not is_admin(message.from_user.id):
        return
    count = await get_user_count()
    await message.answer(f"Uliwma paydalanıwshılar sanı: {count} ta")

@admin_router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    user_count = await get_user_count()
    # Umumiy zakazlar soni (agar bazada zks bo‘lsa)
    total_zks = 0
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT SUM(zks) FROM users")
        row = await cursor.fetchone()
        total_zks = row[0] if row[0] else 0

    await message.answer(
        f" ️Statistika:\n"
        f"Paydalanıwshılar: {user_count}\n"
        f"Jámi buyırtpalar sanı: {total_zks} dana"
    )

# handlers/admin.py — /ads ni to‘liq yangilaymiz

@admin_router.message(Command("ads"))
@admin_only
async def cmd_ads_start(message: Message, state: FSMContext, **kwargs):
    await message.answer("Reklama tekstin jiberiń (keyingi xabarıńız reklama boladı):")
    await state.set_state(AdminStates.waiting_for_ads_text)

@admin_router.message(AdminStates.waiting_for_ads_text)
async def process_ads_text(message: Message, state: FSMContext, bot: Bot, **kwargs):
    ads_text = message.text

    users = await get_all_users()
    if not users:
        await message.answer("Házirshe paydalanıwshılar joq!")
        await state.clear()
        return

    sent = 0
    failed = 0

    for user_id in users:
        try:
            await bot.send_message(user_id, ads_text)
            sent += 1
        except Exception as e:
            failed += 1
            print(f"Qáte {user_id}ģa jiberiwde: {e}")

    await message.answer(
"Reklama jiberildi!\n"
f"Tabıslı: {sent}\n"
f"Jiberilmedi: {failed}"    )
    await state.clear()

@admin_router.message(Command("data"))
@admin_only
async def cmd_data(message: Message, **kwargs):
    csv_data = await export_data()

    file_path = "users_temp.csv"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(csv_data)

    await message.answer_document(
        document=FSInputFile(file_path, filename="users.csv"),
        caption="M Baza (CSV formatta)"
    )
    import os
    os.remove(file_path)

@admin_router.message(Command("pending"))
async def cmd_pending(message: Message):
    if not is_admin(message.from_user.id):
        return
    pending = await get_pending_orders()
    if not pending:
        await message.answer("Kutilayotgan zakazlar yo'q.")
        return
    text = "Kutilayotgan zakazlar:\n\n"
    for order in pending:
        order_id, user_id, direction, phone, lat, lon, created_at = order
        location_link = f"https://maps.google.com/?q={lat},{lon}" if lat and lon else "Lokatsiya yo'q"
        text += f"ID: {order_id}\nTelefon: {phone}\nYo'nalish: {direction}\nLokatsiya: {location_link}\nVaqt: {created_at}\n\n"
    await message.answer(text)

@admin_router.callback_query(F.data.startswith("confirm_"))
async def confirm_order(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    order_id = callback.data.split("_", 1)[1]
    try:
        user_id, old_zks = map(int, order_id.split("_"))
    except ValueError:
        await callback.answer("Naduris order ID!", show_alert=True)
        return

    # Zakaz sonini oshirish
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET zks = zks + 1 WHERE user_id = ?", (user_id,))
        await db.commit()
        cursor = await db.execute("SELECT zks FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        new_zks = row[0] if row else old_zks + 1

    # Foydalanuvchiga xabar
    try:
        await bot.send_message(user_id, f"✅ Zakaz alındı! Jolıńız bolsın.\n\n📊 Zakazlar sanı: {new_zks}")
    except Exception as e:
        print(f"Xato: {e}")

    await callback.message.edit_text(
        callback.message.text + f"\n\n✅ Alındı !\n📊 Zakazlar sanı: {new_zks}",
        reply_markup=None
    )
    await callback.answer("Zakaz alındı!")

@admin_router.callback_query(F.data.startswith("reject_"))
async def cancel_order(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emessiz!", show_alert=True)
        return

    order_id = callback.data.split("_", 1)[1]
    try:
        user_id, zks = map(int, order_id.split("_"))
    except ValueError:
        await callback.answer("Nadurıs order ID!", show_alert=True)
        return

    # Foydalanuvchiga xabar
    try:
        await bot.send_message(user_id, f"❌ Biykar qılındı.\n\n📊 Zakazlar sanı: {zks}")
    except Exception as e:
        print(f"Xato: {e}")

    await callback.message.edit_text(
        callback.message.text + f"\n\n❌ Biykarlandi!\n📊 Zakazlar sanı: {zks}",
        reply_markup=None
    )
    await callback.answer("Buyurtma bekor qilindi!")