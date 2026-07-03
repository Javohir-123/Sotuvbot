# 🐾 Sotish/Sotib olish + Ish e'lonlari Telegram Bot

## 📋 Bot imkoniyatlari

- **🛒 Sotish** — Parrandalar, qora mol, qo'y, ot, mashina, boshqa hayvonlar bo'yicha e'lon joylash
- **🛍 Sotib olish** — Mavjud e'lonlarni ko'rish, sotuvchi kontaktini pullik ko'rish
- **🧑‍💼 Ish berish / 👷 Ishlash** — Ish e'lonlari
- **💳 Balans tizimi** — Chek rasm orqali balansni to'ldirish
- **🤖 Avtomatik chek tekshirish** — Google Vision OCR orqali chekdagi summa va karta raqami tekshiriladi
- **👨‍💼 Admin panel** — Pul berish, xabar yuborish, statistika, chekni qo'lda tasdiqlash/rad etish

---

## 🚀 O'RNATISH VA ISHGA TUSHIRISH (bosqichma-bosqich)

### 1-QADAM: Bot tokenini olish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini va username'ini kiriting (username `bot` bilan tugashi kerak, masalan `MalMolBot`)
4. Sizga token beriladi, masalan: `7123456789:AAHkj3...` — buni saqlab qo'ying

### 2-QADAM: Google Vision API sozlash (chekni avtomatik tekshirish uchun)

Sizda allaqachon `horizontal-data-501009-n0-fbb206898628.json` fayli bor — bu Google Cloud service account kaliti. Lekin **Vision API** yoqilganligini tekshirish kerak:

1. https://console.cloud.google.com ga kiring
2. Loyihangizni tanlang (`horizontal-data-501009-n0`)
3. Chap menyudan **"APIs & Services" → "Library"** ga o'ting
4. Qidiruvga **"Cloud Vision API"** deb yozing va uni oching
5. **"Enable"** tugmasini bosing (agar hali yoqilmagan bo'lsa)
6. **Billing (to'lov)** yoqilganligiga ishonch hosil qiling — Vision API'ning oyiga 1000 tagacha so'rovi bepul, undan keyin pullik

⚠️ **MUHIM XAVFSIZLIK ESLATMASI:** `horizontal-data-501009-n0-fbb206898628.json` fayli — bu maxfiy kalit. Uni:
- Hech qachon GitHub'ga (public repo'ga) yuklamang
- Hech kimga yubormang
- Faqat serveringizga yoki Railway'ning "Secret Files" bo'limiga joylang

### 3-QADAM: Loyihani serverga tayyorlash

Barcha fayllarni bitta papkaga joylashtiring (bu fayllar sizga taqdim etilgan):

```
sotuv_bot/
├── main.py
├── config.py
├── data_lists.py
├── keyboards.py
├── states.py
├── requirements.txt
├── Procfile
├── .env.example
├── .gitignore
├── database/
│   ├── __init__.py
│   └── db.py
├── handlers/
│   ├── __init__.py
│   ├── common.py
│   ├── sell.py
│   ├── buy.py
│   ├── jobs.py
│   ├── payment.py
│   └── admin.py
└── utils/
    ├── __init__.py
    └── ocr_check.py
```

Bunga qo'shimcha ravishda, `google_credentials.json` nomli faylni yarating va ichiga sizning Google service account JSON kalitingizni joylang (bu faylni .gitignore avtomatik chetlab o'tadi).

### 4-QADAM: Railway'ga joylashtirish

1. https://railway.app ga kiring, GitHub akkountingiz bilan ro'yxatdan o'ting
2. Loyihangizni (yuqoridagi fayllar) **yangi GitHub repository**ga yuklang
   - ⚠️ `google_credentials.json` va `.env` fayllarini **hech qachon** GitHub'ga qo'shmang (`.gitignore` bu ishni avtomatik qiladi)
3. Railway'da **"New Project" → "Deploy from GitHub repo"** tugmasini bosing va repongizni tanlang
4. Loyiha ochilgach, **"Variables"** bo'limiga o'ting va quyidagi o'zgaruvchilarni qo'shing:

   | Nomi | Qiymati |
   |------|---------|
   | `BOT_TOKEN` | BotFather'dan olgan tokeningiz |
   | `ADMIN_IDS` | `5492502957` |
   | `ADMIN_USERNAME` | `@Javoh_1hacker` |
   | `CARD_NUMBER` | `6262570040359129` |
   | `MIN_DEPOSIT` | `5000` |
   | `LISTING_PRICE` | `5000` |
   | `VIEW_CONTACT_PRICE` | `5000` |
   | `GOOGLE_CREDENTIALS_PATH` | `google_credentials.json` |

5. `google_credentials.json` faylini yuklash uchun Railway'da **"Settings" → "Config as Code"** yoki loyiha ildiziga fayl sifatida qo'shish kerak. Eng sodda yo'l:
   - Railway loyihangizda **Variables** bo'limiga o'ting
   - **"New Variable" → "Raw Editor"** ni tanlang
   - Yoki muqobil variant: `GOOGLE_CREDENTIALS_JSON` nomli environment variable yaratib, JSON matnining o'zini kiriting, so'ng `main.py` boshida uni faylga yozib qo'yish kodi qo'shiladi (agar shu variant kerak bo'lsa, ayting — kodni moslashtirib beraman)

6. Railway avtomatik ravishda `requirements.txt`'ni o'rnatadi va `Procfile`'dagi buyruq bilan botni ishga tushiradi

7. **"Deployments"** bo'limida loglarni kuzatib, botning xatosiz ishga tushganini tekshiring

### 5-QADAM: Botni sinab ko'rish

1. Telegram'da botingizni toping va `/start` bosing
2. Har bir menyuni sinab ko'ring: Sotish, Sotib olish, Ish berish, Balansni to'ldirish
3. Admin sifatida `/admin` buyrug'ini yuboring (faqat `ADMIN_IDS`da ko'rsatilgan ID uchun ishlaydi)

---

## ⚙️ Sozlamalarni o'zgartirish

- **Narxlarni o'zgartirish**: Railway Variables bo'limida `LISTING_PRICE`, `VIEW_CONTACT_PRICE`, `MIN_DEPOSIT` qiymatlarini o'zgartiring
- **Yangi hayvon/kategoriya qo'shish**: `data_lists.py` faylidagi `CATEGORIES` lug'atiga yangi qator qo'shing
- **Bir nechta admin qo'shish**: `ADMIN_IDS` ga vergul bilan ID qo'shing, masalan `5492502957,123456789`

---

## 🔧 Muammolarni bartaraf etish

**Bot javob bermayapti:**
- Railway loglarida xatolik bor-yo'qligini tekshiring
- `BOT_TOKEN` to'g'ri kiritilganligiga ishonch hosil qiling

**OCR har doim "matn topilmadi" deydi:**
- `GOOGLE_CREDENTIALS_PATH` to'g'ri faylga ishora qilayotganini tekshiring
- Google Cloud Console'da Vision API yoqilganligini va billing faolligini tekshiring
- Chek rasmi sifatli (aniq, yorug', qiyshaymagan) ekanligiga ishonch hosil qiling

**"ModuleNotFoundError" xatosi:**
- `requirements.txt` fayli to'g'ri yuklanganligini va Railway build jarayonini tekshiring

---

## 📌 Muhim eslatmalar

- Bot ma'lumotlari SQLite faylida saqlanadi (`bot_database.db`). Railway'da **persistent volume** yoqmasangiz, har yangi deploy'da baza tozalanishi mumkin — buning oldini olish uchun Railway'da **Volume** qo'shish tavsiya etiladi.
- Hozirgi holatda OCR faqat summa va karta raqamining **oxirgi 4 raqami**ni chekdan qidiradi. Agar cheklaringiz boshqacha formatda bo'lsa (masalan karta raqami umuman ko'rsatilmaydi), `utils/ocr_check.py` faylidagi mantiqni moslashtirish kerak bo'lishi mumkin.
