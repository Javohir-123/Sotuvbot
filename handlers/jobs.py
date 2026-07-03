from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from keyboards import job_view_kb, main_menu_kb
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states import JobPosting, JobBrowsing

router = Router()


# ==================== E'LON JOYLASH (ish berish / ishlash) ====================

@router.message(F.text.in_(["🧑‍💼 Ish berish", "👷 Ishlash"]))
async def job_post_start(message: Message, state: FSMContext):
    await state.clear()
    job_type = "ish_berish" if message.text == "🧑‍💼 Ish berish" else "ishlash"
    await state.update_data(job_type=job_type)
    await state.set_state(JobPosting.entering_title)

    if job_type == "ish_berish":
        await message.answer("🧑‍💼 Qanday ishga xodim kerak? Ish nomini/lavozimini kiriting:")
    else:
        await message.answer("👷 Qanday ish qidiryapsiz? Kasbingiz/yo'nalishingizni kiriting:")


@router.message(JobPosting.entering_title)
async def job_enter_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(JobPosting.entering_description)
    await message.answer("📝 Qo'shimcha ma'lumot kiriting (shartlar, tajriba, talablar va h.k.):")


@router.message(JobPosting.entering_description)
async def job_enter_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(JobPosting.entering_salary)
    await message.answer("💰 Maosh/narxni kiriting (masalan: 3 000 000 so'm yoki \"Kelishiladi\"):")


@router.message(JobPosting.entering_salary)
async def job_enter_salary(message: Message, state: FSMContext):
    await state.update_data(salary=message.text)
    await state.set_state(JobPosting.entering_location)
    await message.answer("📍 Manzil/hududni kiriting (masalan: Toshkent, Chilonzor):")


@router.message(JobPosting.entering_location)
async def job_enter_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(JobPosting.entering_contact_username)
    await message.answer("👤 Telegram username kiriting (masalan @username), bo'lmasa \"yo'q\" deb yozing:")


@router.message(JobPosting.entering_contact_username)
async def job_enter_username(message: Message, state: FSMContext):
    await state.update_data(contact_username=message.text)
    await state.set_state(JobPosting.entering_contact_phone)
    await message.answer("📞 Telefon raqamingizni kiriting:")


@router.message(JobPosting.entering_contact_phone)
async def job_enter_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    job_id = await db.add_job(
        user_id=message.from_user.id,
        job_type=data["job_type"],
        title=data["title"],
        description=data["description"],
        salary=data["salary"],
        location=data["location"],
        contact_username=data["contact_username"],
        contact_phone=message.text
    )
    await state.clear()
    await message.answer(
        f"✅ E'loningiz joylandi! (ID: {job_id})\n\n"
        f"📌 {data['title']}\n"
        f"📝 {data['description']}\n"
        f"💰 {data['salary']}\n"
        f"📍 {data['location']}",
        reply_markup=main_menu_kb()
    )


# ==================== E'LONLARNI KO'RISH ====================
# Foydalanuvchi "ish qidiryapman" bo'limiga kirganda ish beruvchilar ro'yxatini,
# "ish beraman" bo'limiga kirganda esa ishchilarni izlash uchun /find_job kabi buyruq qo'shish mumkin.
# Sodda variant: alohida "Ish e'lonlarini ko'rish" tugmasi orqali kirish.

def job_list_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🧑‍💼 Ish beruvchilarni ko'rish", callback_data="viewjobs_ish_berish")
    builder.button(text="👷 Ish qidiruvchilarni ko'rish", callback_data="viewjobs_ishlash")
    builder.adjust(1)
    return builder.as_markup()


@router.message(F.text == "📋 Ish e'lonlarini ko'rish")
async def job_browse_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📋 Qaysi e'lonlarni ko'rmoqchisiz?", reply_markup=job_list_kb())


def _format_job_text(job):
    return (
        f"📌 <b>{job['title']}</b>\n\n"
        f"📝 {job['description']}\n"
        f"💰 Maosh/narx: {job['salary']}\n"
        f"📍 Manzil: {job['location']}\n\n"
        "Bog'lanish uchun pastdagi tugmani bosing."
    )


@router.callback_query(F.data.startswith("viewjobs_"))
async def view_jobs(callback: CallbackQuery, state: FSMContext):
    job_type = callback.data.replace("viewjobs_", "")
    jobs = await db.get_active_jobs(job_type)

    if not jobs:
        label = "ish beruvchi" if job_type == "ish_berish" else "ish qidiruvchi"
        await callback.message.edit_text(f"😔 Hozircha {label} e'lonlari yo'q.")
        await callback.answer()
        return

    await state.update_data(jobs=jobs, job_index=0)
    await state.set_state(JobBrowsing.browsing)
    await callback.answer()

    job = jobs[0]
    await callback.message.answer(
        _format_job_text(job),
        reply_markup=job_view_kb(job["job_id"], 0, len(jobs)),
        parse_mode="HTML"
    )


@router.callback_query(JobBrowsing.browsing, F.data.startswith("jobnav_"))
async def job_navigate(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.replace("jobnav_", ""))
    data = await state.get_data()
    jobs = data["jobs"]
    job = jobs[index]
    await state.update_data(job_index=index)

    await callback.message.edit_text(
        _format_job_text(job),
        reply_markup=job_view_kb(job["job_id"], index, len(jobs)),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("jobcontact_"))
async def job_view_contact(callback: CallbackQuery):
    job_id = int(callback.data.replace("jobcontact_", ""))
    job = await db.get_job(job_id)
    if not job:
        await callback.answer("⚠️ E'lon topilmadi.", show_alert=True)
        return
    await callback.message.answer(
        f"👤 Lichka: {job['contact_username']}\n"
        f"📞 Telefon: {job['contact_phone']}"
    )
    await callback.answer()
