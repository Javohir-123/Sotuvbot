from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database import db
from keyboards import main_menu_kb
from config import ADMIN_USERNAME

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await db.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "🐾 Hayvon, mashina va boshqa narsalarni sotish/sotib olish botiga xush kelibsiz!\n"
        "Shuningdek bu yerda ish e'lonlarini ham joylashtirishingiz mumkin.\n\n"
        "Quyidagi menyudan kerakli bo'limni tanlang 👇",
        reply_markup=main_menu_kb()
    )


@router.message(F.text == "⬅️ Asosiy menyu")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Asosiy menyu:", reply_markup=main_menu_kb())


@router.message(F.text == "📊 Balans")
async def show_balance(message: Message):
    user = await db.get_user(message.from_user.id)
    balance = user["balance"] if user else 0
    await message.answer(f"📊 Sizning balansingiz: <b>{balance:,} so'm</b>".replace(",", " "), parse_mode="HTML")


@router.message(F.text == "👨‍💼 Admin bilan bog'lanish")
async def contact_admin(message: Message):
    await message.answer(
        f"👨‍💻 Admin bilan bog'lanish: {ADMIN_USERNAME}\n\n"
        "Savollaringiz bo'lsa, bemalol yozishingiz mumkin."
    )
