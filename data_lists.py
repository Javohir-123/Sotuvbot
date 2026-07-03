# Barcha kategoriyalar va ularning ichidagi bo'limlar shu yerda saqlanadi.
# Kengaytirish kerak bo'lsa faqat shu faylni tahrirlash kifoya.

CATEGORIES = {
    "parrandalar": {
        "title": "🐔 Parrandalar",
        "items": {
            "tovuq": "🐔 Tovuq",
            "xoroz": "🐓 Xo'roz",
            "joja": "🐤 Jo'ja",
            "kaklik": "🦃 Kaklik",
            "bedana": "🐦 Bedana",
            "kurka": "🦃 Kurka",
            "ordak": "🦆 O'rdak",
            "goz": "🦢 G'oz",
            "boshqa_parranda": "➕ Boshqa parranda",
        }
    },
    "qora_mol": {
        "title": "🐄 Qora mol",
        "items": {
            "sigir": "🐄 Sigir",
            "buzoq": "🐮 Buzoq",
            "buqa": "🐂 Buqa",
            "ho'kiz": "🐃 Ho'kiz",
            "boshqa_mol": "➕ Boshqa",
        }
    },
    "qoy": {
        "title": "🐑 Qo'y",
        "items": {
            "qoy": "🐑 Qo'y (urg'ochi)",
            "qochqor": "🐏 Qo'chqor",
            "qozi": "🐑 Qo'zi",
            "echki": "🐐 Echki",
            "boshqa_qoy": "➕ Boshqa",
        }
    },
    "ot": {
        "title": "🐎 Ot",
        "items": {
            "ot": "🐎 Ot (erkak)",
            "biya": "🐴 Biya (urg'ochi)",
            "toy": "🐴 Toy",
            "eshak": "🫏 Eshak",
            "boshqa_ot": "➕ Boshqa",
        }
    },
    "mashina": {
        "title": "🚗 Mashina",
        "items": {
            "yengil": "🚗 Yengil avtomobil",
            "yuk": "🚚 Yuk mashinasi",
            "avtobus": "🚌 Avtobus",
            "moto": "🏍 Mototsikl",
            "traktor": "🚜 Traktor / qishloq texnikasi",
            "boshqa_mashina": "➕ Boshqa",
        }
    },
    "boshqa_hayvon": {
        "title": "🐾 Boshqa hayvonlar",
        "items": {
            "it": "🐕 It",
            "mushuk": "🐈 Mushuk",
            "quyon": "🐇 Quyon",
            "baliq": "🐟 Baliq (akvarium)",
            "asalari": "🐝 Asalari (ari oilasi)",
            "boshqa": "➕ Boshqa",
        }
    },
}

# Jins tanlash uchun
GENDERS = ["Erkak", "Urg'ochi", "Aniqlanmagan"]

# Ish e'lonlari turlari
JOB_TYPES = {
    "ish_berish": "🧑‍💼 Ish berish (xodim kerak)",
    "ishlash": "👷 Ishlash (ish qidiryapman)",
}


def get_category_title(cat_key: str) -> str:
    return CATEGORIES.get(cat_key, {}).get("title", cat_key)


def get_item_title(cat_key: str, item_key: str) -> str:
    return CATEGORIES.get(cat_key, {}).get("items", {}).get(item_key, item_key)
