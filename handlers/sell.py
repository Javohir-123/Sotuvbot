from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from keyboards import (
    categories_kb, items_kb, gender_kb, photos_done_kb,
    confirm_listing_kb, main_menu_kb, cancel_kb
)
from data_lists import get_category_title, get_item_title
from states import SellListing, Deposit
from config import FIRST_LISTING_FREE, LISTING_PRICE, CARD_NUMBER, MIN_DEPOSIT

router = Router()


@router.message(F.text == "🛒 Sotish")
async def sell_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(SellListing.choosing_category)
    await message.answer("🛒 Nimani sotmoqchisiz? Kategoriyani tanlang:", reply_markup=categories_kb("sell"))


@router.callback_query(F.data.startswith("sell_cat_"))
async def sell_choose_category(callback: CallbackQuery, state: FSMContext):
    cat_key = callback.data.replace("sell_cat_", "")
    await state.update_data(category=cat_key)
    await state.set_state(SellListing.choosing_item)
    await callback.message.edit_text(
        f"{get_category_title(cat_key)}\n\nQaysi turini sotmoqchisiz?",
        reply_markup=items_kb("sell", cat_key)
    )
    await callback.answer()


@router.callback_query(F.data == "sell_back_categories")
async def sell_back_categories(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SellListing.choosing_category)
    await callback.message.edit_text("🛒 Nimani sotmoqchisiz? Kategoriyani tanlang:", reply_markup=categories_kb("sell"))
    await callback.answer()


@router.callback_query(F.data.startswith("sell_item_"))
async def sell_choose_item(callback: CallbackQuery, state: FSMContext):
    # format: sell_item_{cat_key}_{item_key}
    payload = callback.data.replace("sell_item_", "")
    cat_key, item_key = payload.split("_", 1)
    await state.update_data(subcategory=item_key)
    await state.set_state(SellListing.entering_price)
    await callback.message.edit_text(
        f"✅ Tanlandi: {get_item_title(cat_key, item_key)}\n\n"
        "💰 Narxini kiriting (masalan: 1500000 yoki \"Kelishiladi\"):"
    )
    await callback.answer()


@router.message(SellListing.entering_price)
async def sell_enter_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(SellListing.entering_description)
    await message.answer(
        "📝 Endi mahsulot/hayvon haqida qisqacha ma'lumot yozing\n"
        "(yoshi, holati, qo'shimcha ma'lumotlar va h.k.):"
    )


@router.message(SellListing.entering_description)
async def sell_enter_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text, photos=[])
    await state.set_state(SellListing.uploading_photos)
    await message.answer(
        "📷 Endi 1-3 ta rasm yoki video yuboring.\n"
        "Yuborib bo'lgach, pastdagi tugmani bosing 👇",
        reply_markup=photos_done_kb()
    )


@router.message(SellListing.uploading_photos, F.photo)
async def sell_upload_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 3:
        await message.answer("⚠️ Maksimal 3 ta rasm/video yuborish mumkin. Tugatish uchun tugmani bosing.")
        return
    photos.append(f"photo:{message.photo[-1].file_id}")
    await state.update_data(photos=photos)
    await message.answer(f"✅ Qabul qilindi ({len(photos)}/3). Yana yuborishingiz yoki tugatishingiz mumkin.",
                          reply_markup=photos_done_kb())


@router.message(SellListing.uploading_photos, F.video)
async def sell_upload_video(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 3:
        await message.answer("⚠️ Maksimal 3 ta rasm/video yuborish mumkin. Tugatish uchun tugmani bosing.")
        return
    photos.append(f"video:{message.video.file_id}")
    await state.update_data(photos=photos)
    await message.answer(f"✅ Qabul qilindi ({len(photos)}/3). Yana yuborishingiz yoki tugatishingiz mumkin.",
                          reply_markup=photos_done_kb())


@router.callback_query(SellListing.uploading_photos, F.data == "photos_done")
async def sell_photos_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("photos"):
        await callback.answer("⚠️ Kamida 1 ta rasm yuboring!", show_alert=True)
        return
    await state.set_state(SellListing.choosing_gender)
    await callback.message.edit_text("⚧ Jinsini tanlang:", reply_markup=gender_kb())
    await callback.answer()


@router.callback_query(SellListing.choosing_gender, F.data.startswith("gender_"))
async def sell_choose_gender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data.replace("gender_", "")
    await state.update_data(gender=gender)
    await state.set_state(SellListing.entering_contact_username)
    await callback.message.edit_text(
        "👤 Telegram lichkangizni (username) kiriting.\n"
        "Masalan: @username\n\n"
        "Agar username bo'lmasa, \"yo'q\" deb yozing:"
    )
    await callback.answer()


@router.message(SellListing.entering_contact_username)
async def sell_enter_username(message: Message, state: FSMContext):
    await state.update_data(contact_username=message.text)
    await state.set_state(SellListing.entering_contact_phone)
    await message.answer("📞 Endi telefon raqamingizni kiriting.\nMasalan: +998901234567")


@router.message(SellListing.entering_contact_phone)
async def sell_enter_phone(message: Message, state: FSMContext):
    await state.update_data(contact_phone=message.text)
    data = await state.get_data()
    await state.set_state(SellListing.confirming)

    cat_key = data["category"]
    item_key = data["subcategory"]

    text = (
        "📋 <b>E'lon ma'lumotlari:</b>\n\n"
        f"📂 Turkum: {get_category_title(cat_key)} — {get_item_title(cat_key, item_key)}\n"
        f"💰 Narxi: {data['price']}\n"
        f"📝 Ma'lumot: {data['description']}\n"
        f"⚧ Jinsi: {data['gender']}\n"
        f"👤 Lichka: {data['contact_username']}\n"
        f"📞 Raqam: {data['contact_phone']}\n"
        f"📷 Media: {len(data.get('photos', []))} ta\n\n"
        "Hammasi to'g'rimi?"
    )
    await message.answer(text, reply_markup=confirm_listing_kb(), parse_mode="HTML")


@router.callback_query(SellListing.confirming, F.data == "listing_cancel")
async def sell_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ E'lon bekor qilindi.")
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(SellListing.confirming, F.data == "listing_confirm")
async def sell_confirm(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    data = await state.get_data()

    needs_payment = True
    if FIRST_LISTING_FREE and user and user["free_listing_used"] == 0:
        needs_payment = False

    if needs_payment and user["balance"] < LISTING_PRICE:
        await state.set_state(SellListing.waiting_payment)
        await callback.message.edit_text(
            f"💳 E'lon joylash uchun {LISTING_PRICE:,} so'm to'lov talab qilinadi.\n"
            f"Sizning balansingiz: {user['balance']:,} so'm yetarli emas.\n\n"
            "Balansni to'ldirish uchun \"💳 Balansni to'ldirish\" tugmasini bosing."
            .replace(",", " "),
        )
        await callback.answer()
        return

    # E'lonni saqlash
    photos_str = ",".join(data.get("photos", []))
    listing_id = await db.add_listing(
        user_id=user_id,
        category=data["category"],
        subcategory=data["subcategory"],
        price=data["price"],
        description=data["description"],
        gender=data["gender"],
        contact_username=data["contact_username"],
        contact_phone=data["contact_phone"],
        photos=photos_str
    )

    if needs_payment:
        await db.update_balance(user_id, -LISTING_PRICE)
    else:
        await db.set_free_listing_used(user_id)

    await state.clear()
    if needs_payment:
        extra_line = f"💳 Balansingizdan {LISTING_PRICE:,} so'm yechildi.".replace(",", " ")
    else:
        extra_line = "🎁 Birinchi e'loningiz bepul joylandi."

    await callback.message.edit_text(
        f"✅ E'loningiz muvaffaqiyatli joylandi! (ID: {listing_id})\n{extra_line}"
    )
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=main_menu_kb())
    await callback.answer()
