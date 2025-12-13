import aiosqlite

from aiogram import Router, F, Bot  
from aiogram.types import Message, Location
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import HELP_LINK, DB_NAME, ADMIN_ID
from database import user_exists, add_user, get_user_by_phone, update_phone, get_zks, add_order, get_phone
from states import RegisterState, ChangePhoneState, DirectionState, LocationState
from keyboards.reply import get_direction_menu, get_location_menu
from keyboards.inline import get_admin_confirm
from utils import is_admin, format_order_message

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("Sálem, Brat! Bot iske tústi.")
        return

    exists = await user_exists(message.from_user.id)
    if exists:
        await message.answer(f"Siz aldın dizimnen ótkensiz. Sálem, {message.from_user.first_name}!")
        await state.clear()
        await state.set_state(DirectionState.choose)
        await message.answer("Qayaqqa baramız?", reply_markup=get_direction_menu())
    else:
        await state.set_state(RegisterState.phone_number)
        await message.answer(
            f"Assalawma aleykum! {message.from_user.first_name}\n"
                "Siz benen baylanısıw ushın telefon nomerińizdi kirgiziń:\n"
                "Mısalı: 991234125"
        )

@user_router.message(RegisterState.phone_number, F.text)
async def register_phone(message: Message, state: FSMContext):
    phone_number = message.text.strip()
    if not phone_number.isdigit() or len(phone_number) != 9:
        await message.answer("Naduris nomer! 9 cifr teriń, mısalı: 991234125")
        return

    existing = await get_user_by_phone(phone_number)
    if existing:
        await message.answer("Bul nomer dizimnen ótken!")
        return

    await add_user(message.from_user.id, message.from_user.first_name, phone_number)
    await message.answer("Maǵlıwmatlarıńız tabıslı saqlandı!")
    await state.clear()
    await state.set_state(DirectionState.choose)
    await message.answer("Qayaqqa baramız?", reply_markup=get_direction_menu())

@user_router.message(DirectionState.choose, F.text.in_({"Shımbayǵa", "Nókiske"}))
async def choose_direction(message: Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await state.set_state(LocationState.send)
    await message.answer("Lokatsiya jiberiń:", reply_markup=get_location_menu())

@user_router.message(LocationState.send, F.text == "Biykarlaw")
async def cancel_location(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(DirectionState.choose)
    await message.answer("Biykarlandı. Qayaqqa baramız?", reply_markup=get_direction_menu())

@user_router.message(LocationState.send, F.location)
async def receive_location(message: Message, state: FSMContext, bot: Bot):
    location = message.location
    lat = location.latitude
    lon = location.longitude

    # Bazaga location saqlash shart emas, faqat admin ga yuborish
    data = await state.get_data()
    direction = data.get("direction")
    phone_number = await get_phone(message.from_user.id)
    zks = await get_zks(message.from_user.id)

    order_id = f"{message.from_user.id}_{zks}"

    # Admin ga yuborish
    order_message = format_order_message(phone_number, direction, zks, lat, lon)
    try:
        await bot.send_message(ADMIN_ID, order_message, reply_markup=get_admin_confirm(order_id))
        await message.answer("Qabıllandı.")
    except Exception as e:
        print(f"Admin ge zakaz jiberiwde qátelik: {e}")
        await message.answer("Qátelik. Qayta urınıp kóriń.")

    await state.clear()
    await state.set_state(DirectionState.choose)
    await message.answer(
        "Adminge jiberildi. Biraz kútip turıń!",
        reply_markup=get_direction_menu()
    )

@user_router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(f"járdem: {HELP_LINK}")

@user_router.message(Command("zakazs"))
async def cmd_zakazs(message: Message):
    zks = await get_zks(message.from_user.id)
    await message.answer(f"Zakazlar sanı: {zks}")

@user_router.message(Command("changenumber"))
async def cmd_changenumber(message: Message, state: FSMContext):
    await state.set_state(ChangePhoneState.new_phone)
    await message.answer("Taza telefon nomer kirgiziń:")

@user_router.message(ChangePhoneState.new_phone, F.text)
async def update_new_phone(message: Message, state: FSMContext):
    new_phone = message.text.strip()
    if not new_phone.isdigit() or len(new_phone) != 9:
        await message.answer("Nadurıs nomer! 9 cifr kirgiziń.")
        return

    await update_phone(message.from_user.id, new_phone)
    await message.answer("Telefon nomerińiz tabıslı ózgerdi!")
    await state.clear()
    await state.set_state(DirectionState.choose)
    await message.answer("Qayaqqa baramız?", reply_markup=get_direction_menu())

@user_router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(DirectionState.choose)
    await message.answer("Qayaqqa baramız?", reply_markup=get_direction_menu())

@user_router.message(F.text == "Bosh menyu")
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(DirectionState.choose)
    await message.answer("Qayaqqa baramız?", reply_markup=get_direction_menu())