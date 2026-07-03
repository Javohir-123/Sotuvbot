from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import db
from keyboards import admin_reply_kb, main_menu_kb
from states import AdminGiveMoney, AdminBroadcast
from config import ADMIN_IDS

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(F.text == "/admin")
async def admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("🔐 Boshqaruv paneli", reply_markup=admin_reply_kb())


@router.message(F.text == "💰 Pul berish")
async def admin_give_money_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminGiveMoney.entering_user_id)
    await message.answer("Foydalanuvchi ID raqamini kiriting:")


@router.message(AdminGiveMoney.entering_user_id)
async def admin_give_money_id(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("ID faqat raqamlardan iborat bo'lishi kerak:")
        return
    await state.update_data(target_id=int(message.text.strip()))
    await state.set_state(AdminGiveMoney.entering_amount)
    await message.answer("Qo'shiladigan summani kiriting (so'mda, faqat raqam):")


@router.message(AdminGiveMoney.entering_amount)
async def admin_give_money_amount(message: Message, state: FSMContext, bot: Bot):
    text = message.text.strip().replace(" ", "")
    if not text.lstrip("-").isdigit():
        await message.answer("Summani faqat raqamlarda kiriting:")
        return

    amount = int(text)
    data = await state.get_data()
    target_id = data["target_id"]

    user = await db.get_user(target_id)
    if not user:
        await message.answer("⚠️ Bunday foydalanuvchi topilmadi.")
        await state.clear()
        return

    await db.update_balance(target_id, amount)
    await state.clear()

    await message.answer(
        f"✅ {target_id} foydalanuvchiga {amount:,} so'm qo'shildi.".replace(",", " "),
        reply_markup=admin_reply_kb()
    )
    try:
        await bot.send_message(target_id, f"💰 Balansingizga admin tomonidan {amount:,} so'm qo'shildi.".replace(",", " "))
    except Exception:
        pass


@router.message(F.text == "✉️ Xabar yuborish")
async def admin_broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminBroadcast.entering_user_id)
    await message.answer(
        "Foydalanuvchi ID raqamini kiriting (barchaga yuborish uchun \"all\" deb yozing):"
    )


@router.message(AdminBroadcast.entering_user_id)
async def admin_broadcast_id(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() != "all" and not text.isdigit():
        await message.answer("ID faqat raqamlardan iborat bo'lishi kerak yoki \"all\" deb yozing:")
        return
    await state.update_data(target=text)
    await state.set_state(AdminBroadcast.entering_message)
    await message.answer("Yubormoqchi bo'lgan xabar matnini kiriting:")


@router.message(AdminBroadcast.entering_message)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target = data["target"]
    text = message.text

    if target == "all":
        users = await db.get_all_users()
        sent = 0
        for u in users:
            try:
                await bot.send_message(u["user_id"], text)
                sent += 1
            except Exception:
                pass
        await message.answer(f"✅ Xabar {sent} ta foydalanuvchiga yuborildi.", reply_markup=admin_reply_kb())
    else:
        try:
            await bot.send_message(int(target), text)
            await message.answer("✅ Xabar yuborildi.", reply_markup=admin_reply_kb())
        except Exception:
            await message.answer("⚠️ Xabar yuborib bo'lmadi. Foydalanuvchi botni bloklagan bo'lishi mumkin.",
                                  reply_markup=admin_reply_kb())

    await state.clear()


@router.message(F.text == "📈 Statistika")
async def admin_stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    users_count = await db.count_users()
    total_deposits = await db.sum_deposits()
    listings_count = await db.count_listings()

    await message.answer(
        "📈 Bot Statistikasi:\n\n"
        f"👥 A'zolar: {users_count} ta\n"
        f"💰 Jami kiritilgan pul: {total_deposits:,} so'm\n"
        f"📦 Faol e'lonlar: {listings_count} ta".replace(",", " ")
    )
