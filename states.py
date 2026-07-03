from aiogram.fsm.state import State, StatesGroup


class SellListing(StatesGroup):
    choosing_category = State()
    choosing_item = State()
    entering_price = State()
    entering_description = State()
    uploading_photos = State()
    choosing_gender = State()
    entering_contact_username = State()
    entering_contact_phone = State()
    confirming = State()
    waiting_payment = State()


class BuyBrowsing(StatesGroup):
    choosing_category = State()
    choosing_item = State()
    browsing = State()


class JobPosting(StatesGroup):
    choosing_type = State()
    entering_title = State()
    entering_description = State()
    entering_salary = State()
    entering_location = State()
    entering_contact_username = State()
    entering_contact_phone = State()
    confirming = State()


class JobBrowsing(StatesGroup):
    choosing_type = State()
    browsing = State()


class Deposit(StatesGroup):
    entering_amount = State()
    waiting_receipt = State()


class AdminGiveMoney(StatesGroup):
    entering_user_id = State()
    entering_amount = State()


class AdminBroadcast(StatesGroup):
    entering_user_id = State()
    entering_message = State()
