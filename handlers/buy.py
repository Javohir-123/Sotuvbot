from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram.fsm.context import FSMContext

from database import db
from keyboards import categories_kb, items_kb, listing_view_kb, main_menu_kb
from data_lists import get_category_title, get_item_title
from states import BuyBrowsing
from config import VIEW_CONTACT_PRICE

router = Router()


@router.message(F.text == "🛍 Sotib olish")
async def buy_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(BuyBrowsing.choosing_category)
    await message.answer("🛍 Nimani sotib olmoqchisiz? Kategoriyani tanlang:", reply_markup=categories_kb("buy"))


@router.callback_query(F.data.startswith("buy_cat_"))
async def buy_choose_category(callback: CallbackQuery, state: FSMContext):
    cat_key = callback.data.replace("buy_cat_", "")
    await state.update_data(category=cat_key)
    await state.set_state(BuyBrowsing.choosing_item)
    await callback.message.edit_text(
        f"{get_category_title(cat_key)}\n\nQaysi turini qidiryapsiz?",
        reply_markup=items_kb("buy", cat_key)
    )
    await callback.answer()


@router.callback_query(F.data == "buy_back_categories")
async def buy_back_categories(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BuyBrowsing.choosing_category)
    await callback.message.edit_text("🛍 Nimani sotib olmoqchisiz? Kategoriyani tanlang:", reply_markup=categories_kb("buy"))
    await callback.answer()


def _format_listing_text(listing, cat_key, item_key):
    return (
        f"{get_item_title(cat_key, item_key)}\n\n"
        f"💰 Narxi: {listing['price']}\n"
        f"📝 Ma'lumot: {listing['description']}\n"
        f"⚧ Jinsi: {listing['gender']}\n\n"
        f"📞 Sotib olish uchun pastdagi tugmani bosing va egasi bilan bog'laning."
    )


async def _show_listing(target, state: FSMContext, index: int, edit=False):
    """target - Message yoki CallbackQuery.message"""
    data = await state.get_data()
    listings = data.get("listings", [])
    cat_key = data.get("category")
    item_key = data.get("item")

    if not listings:
        return

    listing = listings[index]
    text = _format_listing_text(listing, cat_key, item_key)
    kb = listing_view_kb(listing["listing_id"], index, len(listings))

    photos = listing["photos"].split(",") if listing["photos"] else []

    if photos:
        first_type, first_id = photos[0].split(":", 1)
        if first_type == "photo":
            await target.answer_photo(first_id, caption=text, reply_markup=kb)
        else:
            await target.answer_video(first_id, caption=text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("buy_item_"))
async def buy_choose_item(callback: CallbackQuery, state: FSMContext):
    payload = callback.data.replace("buy_item_", "")
    cat_key, item_key = payload.split("_", 1)

    listings = await db.get_active_listings(cat_key, item_key)

    if not listings:
        await callback.message.edit_text(
            f"😔 Hozircha sotiladigan \"{get_item_title(cat_key, item_key)}\" yo'q.\n\n"
            "Keyinroq qayta urinib ko'ring yoki boshqa turkumni tanlang.",
            reply_markup=items_kb("buy", cat_key)
        )
        await callback.answer()
        return

    await state.update_data(category=cat_key, item=item_key, listings=listings, index=0)
    await state.set_state(BuyBrowsing.browsing)
    await callback.answer()
    await _show_listing(callback.message, state, 0)


@router.callback_query(BuyBrowsing.browsing, F.data.startswith("nav_"))
async def buy_navigate(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.replace("nav_", ""))
    await state.update_data(index=index)
    data = await state.get_data()
    listings = data["listings"]
    cat_key = data["category"]
    item_key = data["item"]

    listing = listings[index]
    text = _format_listing_text(listing, cat_key, item_key)
    kb = listing_view_kb(listing["listing_id"], index, len(listings))
    photos = listing["photos"].split(",") if listing["photos"] else []

    try:
        if photos:
            first_type, first_id = photos[0].split(":", 1)
            if first_type == "photo":
                media = InputMediaPhoto(media=first_id, caption=text)
            else:
                media = InputMediaVideo(media=first_id, caption=text)
            await callback.message.edit_media(media=media, reply_markup=kb)
        else:
            await callback.message.edit_text(text, reply_markup=kb)
    except Exception:
        # Agar edit ishlamasa (masalan matn->media almashinuvi), yangi xabar yuboramiz
        await _show_listing(callback.message, state, index)

    await callback.answer()


@router.callback_query(F.data.startswith("viewcontact_"))
async def buy_view_contact(callback: CallbackQuery, state: FSMContext):
    listing_id = int(callback.data.replace("viewcontact_", ""))
    user_id = callback.from_user.id

    already_viewed = await db.has_viewed_contact(user_id, listing_id)
    listing = await db.get_listing(listing_id)

    if not listing or listing["status"] != "active":
        await callback.answer("⚠️ Bu e'lon endi mavjud emas.", show_alert=True)
        return

    if already_viewed:
        await callback.message.answer(
            f"👤 Sotuvchi lichkasi: {listing['contact_username']}\n"
            f"📞 Telefon raqami: {listing['contact_phone']}"
        )
        await callback.answer()
        return

    user = await db.get_user(user_id)
    if user["balance"] < VIEW_CONTACT_PRICE:
        await callback.answer(
            f"💳 Sotuvchi egasini ko'rish uchun {VIEW_CONTACT_PRICE:,} so'm kerak.\n"
            "Balansingizni to'ldiring.".replace(",", " "),
            show_alert=True
        )
        return

    await db.update_balance(user_id, -VIEW_CONTACT_PRICE)
    await db.add_contact_view(user_id, listing_id)

    await callback.message.answer(
        f"✅ To'lov amalga oshirildi ({VIEW_CONTACT_PRICE:,} so'm yechildi).\n\n"
        f"👤 Sotuvchi lichkasi: {listing['contact_username']}\n"
        f"📞 Telefon raqami: {listing['contact_phone']}".replace(",", " ")
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()
