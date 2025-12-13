# database.py - aiosqlite bilan async baza funksiyalari
import aiosqlite
from datetime import datetime
from config import DB_NAME

async def init_db():
    """Baza va jadval yaratish"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                phone_number TEXT UNIQUE,  -- Takrorlanmaslik uchun UNIQUE
                zks INTEGER DEFAULT 0,
                join_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    print("Baza tayyor!")

async def user_exists(user_id: int) -> bool:
    """User mavjudligini tekshirish"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone() is not None

async def get_user_by_phone(phone_number: str) -> dict:
    """Telefon bo'yicha user olish (takror tekshirish uchun)"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,))
        row = await cursor.fetchone()
        if row:
            return {"user_id": row[0], "username": row[1], "phone_number": row[2], "zks": row[3]}
        return None

async def add_user(user_id: int, username: str, phone_number: str):
    """User qo'shish, takror bo'lsa qo'shmaydi"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, phone_number) VALUES (?, ?, ?)",
            (user_id, username, phone_number)
        )
        await db.commit()

async def update_phone(user_id: int, new_phone: str):
    """Telefon raqamni yangilash"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET phone_number = ? WHERE user_id = ?",
            (new_phone, user_id)
        )
        await db.commit()

async def update_zks(user_id: int, increment: int = 1):
    """ZKS ni oshirish"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET zks = zks + ? WHERE user_id = ?",
            (increment, user_id)
        )
        await db.commit()

async def get_zks(user_id: int) -> int:
    """ZKS olish"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT zks FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0

async def get_user_count() -> int:
    """Foydalanuvchilar soni"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0]

async def get_all_users() -> list:
    """Hamma user ID'lar (ads uchun)"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        return [row[0] for row in await cursor.fetchall()]

async def export_data() -> str:
    """Baza export (CSV formatda string qaytarish)"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT * FROM users")
        rows = await cursor.fetchall()
        csv_data = "user_id,username,phone_number,zks,join_date\n"
        for row in rows:
            csv_data += ",".join(map(str, row)) + "\n"
        return csv_data

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                phone_number TEXT,
                zks INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def add_order(user_id, direction, phone_number, lat, lon):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO orders (user_id, direction, phone_number, location_lat, location_lon)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, direction, phone_number, lat, lon))
        order_id = cursor.lastrowid
        await db.commit()
        return order_id

async def update_order_status(order_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        await db.commit()

async def get_pending_orders():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT id, user_id, direction, phone_number, location_lat, location_lon, created_at
            FROM orders WHERE status = 'pending' ORDER BY created_at DESC
        """)
        return await cursor.fetchall()

async def get_order_by_id(order_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        return await cursor.fetchone()

async def get_phone(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT phone_number FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else None