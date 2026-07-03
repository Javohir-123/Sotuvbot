import aiosqlite
import datetime
from config import DB_PATH

# ==================== BAZANI YARATISH ====================

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchilar
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            phone TEXT,
            balance INTEGER DEFAULT 0,
            free_listing_used INTEGER DEFAULT 0,
            joined_at TEXT
        )
        """)

        # E'lonlar (sotish e'lonlari - hayvon/mashina va h.k.)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            listing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,          -- masalan: parrandalar, qora_mol, ot, mashina...
            subcategory TEXT,       -- masalan: tovuq, xo'roz...
            price TEXT,
            description TEXT,
            gender TEXT,            -- jinsi
            contact_username TEXT,  -- lichkasi
            contact_phone TEXT,     -- raqami
            photos TEXT,            -- vergul bilan ajratilgan file_id lar
            status TEXT DEFAULT 'active',  -- active / sold / removed
            created_at TEXT
        )
        """)

        # Ish e'lonlari (ish berish / ishlash)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            job_type TEXT,          -- 'ish_berish' yoki 'ishlash'
            title TEXT,
            description TEXT,
            salary TEXT,
            location TEXT,
            contact_username TEXT,
            contact_phone TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT
        )
        """)

        # Depozitlar / chek tarixi
        await db.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            deposit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            photo_file_id TEXT,
            status TEXT DEFAULT 'pending',  -- pending / approved / rejected
            reason TEXT,
            created_at TEXT
        )
        """)

        # Kontakt ko'rishlar tarixi (kim qaysi e'lon egasini ko'rdi)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS contact_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            listing_id INTEGER,
            viewed_at TEXT
        )
        """)

        await db.commit()


# ==================== FOYDALANUVCHILAR ====================

async def add_user(user_id, full_name, username):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if not row:
            await db.execute(
                "INSERT INTO users (user_id, full_name, username, balance, joined_at) VALUES (?, ?, ?, 0, ?)",
                (user_id, full_name, username, datetime.datetime.now().isoformat())
            )
            await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cur.fetchone()


async def update_balance(user_id, amount):
    """amount musbat bo'lsa qo'shadi, manfiy bo'lsa ayiradi"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()


async def set_free_listing_used(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET free_listing_used = 1 WHERE user_id = ?", (user_id,))
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users")
        return await cur.fetchall()


async def count_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        row = await cur.fetchone()
        return row[0]


# ==================== E'LONLAR (Sotish) ====================

async def add_listing(user_id, category, subcategory, price, description,
                       gender, contact_username, contact_phone, photos):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO listings 
            (user_id, category, subcategory, price, description, gender, contact_username, contact_phone, photos, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
        """, (user_id, category, subcategory, price, description, gender,
              contact_username, contact_phone, photos, datetime.datetime.now().isoformat()))
        await db.commit()
        return cur.lastrowid


async def get_active_listings(category, subcategory):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT * FROM listings 
            WHERE category = ? AND subcategory = ? AND status = 'active'
            ORDER BY created_at DESC
        """, (category, subcategory))
        return await cur.fetchall()


async def get_listing(listing_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM listings WHERE listing_id = ?", (listing_id,))
        return await cur.fetchone()


async def count_listings():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM listings WHERE status='active'")
        row = await cur.fetchone()
        return row[0]


# ==================== ISH E'LONLARI ====================

async def add_job(user_id, job_type, title, description, salary, location,
                   contact_username, contact_phone):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO jobs
            (user_id, job_type, title, description, salary, location, contact_username, contact_phone, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
        """, (user_id, job_type, title, description, salary, location,
              contact_username, contact_phone, datetime.datetime.now().isoformat()))
        await db.commit()
        return cur.lastrowid


async def get_active_jobs(job_type):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT * FROM jobs WHERE job_type = ? AND status = 'active' ORDER BY created_at DESC
        """, (job_type,))
        return await cur.fetchall()


async def get_job(job_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        return await cur.fetchone()


# ==================== DEPOZITLAR ====================

async def create_deposit(user_id, amount, photo_file_id, status="pending", reason=""):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO deposits (user_id, amount, photo_file_id, status, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, amount, photo_file_id, status, reason, datetime.datetime.now().isoformat()))
        await db.commit()
        return cur.lastrowid


async def update_deposit_status(deposit_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE deposits SET status = ? WHERE deposit_id = ?", (status, deposit_id))
        await db.commit()


async def get_deposit(deposit_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM deposits WHERE deposit_id = ?", (deposit_id,))
        return await cur.fetchone()


async def count_deposits():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM deposits WHERE status='approved'")
        row = await cur.fetchone()
        return row[0]


async def sum_deposits():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT SUM(amount) FROM deposits WHERE status='approved'")
        row = await cur.fetchone()
        return row[0] or 0


# ==================== KONTAKT KO'RISHLAR ====================

async def has_viewed_contact(user_id, listing_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id FROM contact_views WHERE user_id = ? AND listing_id = ?",
            (user_id, listing_id)
        )
        row = await cur.fetchone()
        return row is not None


async def add_contact_view(user_id, listing_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO contact_views (user_id, listing_id, viewed_at) VALUES (?, ?, ?)",
            (user_id, listing_id, datetime.datetime.now().isoformat())
        )
        await db.commit()
