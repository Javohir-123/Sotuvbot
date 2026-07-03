import os
from dotenv import load_dotenv

load_dotenv()

# --- Bot sozlamalari ---
BOT_TOKEN = os.getenv("BOT_TOKEN")  # @BotFather dan olinadi

# --- Admin sozlamalari ---
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "5492502957").split(",") if x]
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@Javoh_1hacker")

# --- To'lov sozlamalari ---
CARD_NUMBER = os.getenv("CARD_NUMBER", "6262570040359129")
CARD_OWNER = os.getenv("CARD_OWNER", "")  # Karta egasi ismi (chekda tekshirish uchun, ixtiyoriy)
MIN_DEPOSIT = int(os.getenv("MIN_DEPOSIT", "5000"))

# --- E'lon narxlari ---
FIRST_LISTING_FREE = True          # Birinchi e'lon bepul
LISTING_PRICE = int(os.getenv("LISTING_PRICE", "5000"))  # Keyingi e'lonlar narxi
VIEW_CONTACT_PRICE = int(os.getenv("VIEW_CONTACT_PRICE", "5000"))  # Sotuvchi kontaktini ko'rish narxi

# --- Google Vision OCR ---
# Ikki usuldan biri bilan beriladi:
# 1) GOOGLE_CREDENTIALS_JSON - JSON matnining o'zi (Railway Variables'ga to'g'ridan-to'g'ri nusxalanadi)
# 2) GOOGLE_CREDENTIALS_PATH - fayl manzili (agar serverga fayl sifatida yuklangan bo'lsa)
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "google_credentials.json")

# --- Ma'lumotlar bazasi ---
DB_PATH = os.getenv("DB_PATH", "bot_database.db")
