import re
import logging
from google.cloud import vision
from google.oauth2 import service_account
from config import GOOGLE_CREDENTIALS_PATH, CARD_NUMBER

logger = logging.getLogger(__name__)

_credentials = None
_client = None


def _get_client():
    global _credentials, _client
    if _client is None:
        _credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH)
        _client = vision.ImageAnnotatorClient(credentials=_credentials)
    return _client


def _extract_text(image_bytes: bytes) -> str:
    """Google Vision orqali rasmdan matn ajratib oladi"""
    client = _get_client()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    if response.error.message:
        raise Exception(response.error.message)
    texts = response.text_annotations
    if not texts:
        return ""
    return texts[0].description


def _normalize_digits(text: str) -> str:
    """Matndagi barcha raqamlarni bitta uzun qatorga aylantiradi (bo'sh joy, chiziqcha olib tashlanadi)"""
    return re.sub(r"\D", "", text)


def _find_amounts(text: str):
    """Matndan pul summalarini topadi (masalan: 5 000, 15,000, 5000 so'm)"""
    # 3+ xonali raqamlar, orasida bo'shliq/vergul/nuqta bo'lishi mumkin
    pattern = r"\d{1,3}(?:[ .,]\d{3})+|\d{4,}"
    matches = re.findall(pattern, text)
    amounts = []
    for m in matches:
        digits = re.sub(r"[ .,]", "", m)
        if digits.isdigit():
            amounts.append(int(digits))
    return amounts


def check_receipt(image_bytes: bytes, expected_amount: int):
    """
    Chek rasmini tekshiradi.
    Qaytaradi: (approved: bool, reason: str)
    """
    try:
        text = _extract_text(image_bytes)
    except Exception as e:
        logger.error(f"OCR xatosi: {e}")
        return False, "❌ Rasmni tahlil qilishda texnik xatolik yuz berdi."

    if not text or len(text.strip()) < 3:
        return False, "❌ Rasmdan matn topilmadi. Aniqroq rasm yuboring."

    clean_text = _normalize_digits(text)
    card_last4 = CARD_NUMBER[-4:]
    card_found = card_last4 in clean_text or CARD_NUMBER in clean_text

    amounts = _find_amounts(text)
    amount_found = expected_amount in amounts

    if amount_found and card_found:
        return True, "✅ Summa va karta raqami mos keldi."
    elif amount_found and not card_found:
        return False, "⚠️ Summa topildi, lekin karta raqami cheklarda aniqlanmadi."
    elif card_found and not amount_found:
        return False, f"⚠️ Karta raqami topildi, lekin {expected_amount:,} so'm summasi aniqlanmadi.".replace(",", " ")
    else:
        return False, "❌ Chekda kerakli summa yoki karta raqami topilmadi."
