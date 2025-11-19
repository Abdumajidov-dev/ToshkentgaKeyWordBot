"""
Duplicate Remover Bot - Takroriy habarlarni avtomatik o'chirish

Vazifasi:
- Target guruhlardagi takroriy habarlarni aniqlash
- Birinchi habarni saqlash, keyingilari o'chirish
- Message hash asosida ishlaydi (text + media fayl ID)

Author: Abdumajid
"""

import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from core.config import DUPLICATE_REMOVER_TOKEN, ADMIN_IDS
from core.storage import load_state
import json
import os

# Bot va Dispatcher
bot = Bot(token=DUPLICATE_REMOVER_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ============================================================
# MESSAGE HASH STORAGE
# ============================================================
# Format: {group_id: {message_hash: {"first_message_id": int, "timestamp": float, "count": int}}}
message_hashes = {}

# Tozalash vaqti: 24 soat (eski xashlar avtomatik o'chiriladi)
HASH_EXPIRY_HOURS = 24

# Duplicate cache file
DUPLICATE_CACHE_FILE = "data/duplicate_cache.json"


def load_duplicate_cache():
    """Cache'ni fayldan yuklash"""
    global message_hashes
    try:
        if os.path.exists(DUPLICATE_CACHE_FILE):
            with open(DUPLICATE_CACHE_FILE, 'r', encoding='utf-8') as f:
                message_hashes = json.load(f)
            print(f"[OK] Duplicate cache yuklandi: {len(message_hashes)} guruh")
        else:
            message_hashes = {}
            print("[INFO] Yangi duplicate cache yaratildi")
    except Exception as e:
        print(f"[OGOHLANTIRISH] Cache yuklash xatolik: {e}")
        message_hashes = {}


def save_duplicate_cache():
    """Cache'ni faylga saqlash"""
    try:
        with open(DUPLICATE_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(message_hashes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[OGOHLANTIRISH] Cache saqlash xatolik: {e}")


def get_message_hash(message: types.Message) -> str:
    """
    Xabar uchun unikal hash yaratish

    Hash komponentlari:
    - Text matn (agar mavjud bo'lsa)
    - Photo file_id (agar photo bo'lsa)
    - Video file_id (agar video bo'lsa)
    - Document file_id (agar document bo'lsa)
    - Caption (agar mavjud bo'lsa)
    """
    components = []

    # Text
    if message.text:
        components.append(message.text.strip().lower())

    # Caption
    if message.caption:
        components.append(message.caption.strip().lower())

    # Media file IDs
    if message.photo:
        # Eng katta o'lchamdagi photo
        components.append(message.photo[-1].file_id)

    if message.video:
        components.append(message.video.file_id)

    if message.document:
        components.append(message.document.file_id)

    if message.audio:
        components.append(message.audio.file_id)

    if message.voice:
        components.append(message.voice.file_id)

    if message.sticker:
        components.append(message.sticker.file_id)

    # Hash yaratish
    if not components:
        # Bo'sh xabar (masalan, faqat emoji)
        return None

    hash_string = "|".join(components)
    return hashlib.md5(hash_string.encode()).hexdigest()


def cleanup_old_hashes():
    """24 soatdan eski xashlarni tozalash"""
    global message_hashes
    current_time = time.time()
    expiry_seconds = HASH_EXPIRY_HOURS * 3600

    cleaned_count = 0
    for group_id in list(message_hashes.keys()):
        group_hashes = message_hashes[group_id]

        # Eski xashlarni o'chirish
        for msg_hash in list(group_hashes.keys()):
            if current_time - group_hashes[msg_hash]["timestamp"] > expiry_seconds:
                del group_hashes[msg_hash]
                cleaned_count += 1

        # Bo'sh guruhni o'chirish
        if not group_hashes:
            del message_hashes[group_id]

    if cleaned_count > 0:
        print(f"[CLEANUP] {cleaned_count} ta eski hash o'chirildi")
        save_duplicate_cache()


# ============================================================
# MESSAGE HANDLERS
# ============================================================

@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_message(message: types.Message):
    """Guruh xabarlarini tekshirish va takroriylarni o'chirish"""

    # Faqat target guruhlarda ishlash
    state_data = load_state()
    target_groups = state_data.get("target_groups", [])

    # Group ID ni string formatga o'tkazish (target_groups list'ida string formatda)
    group_id_str = str(message.chat.id)

    if group_id_str not in target_groups:
        # Bu target guruh emas, ignore qilish
        return

    # Message hash yaratish
    msg_hash = get_message_hash(message)

    if not msg_hash:
        # Hash yaratib bo'lmadi (bo'sh xabar)
        return

    # Group uchun hash storage yaratish (agar yo'q bo'lsa)
    if group_id_str not in message_hashes:
        message_hashes[group_id_str] = {}

    group_hashes = message_hashes[group_id_str]

    # Hash mavjudligini tekshirish
    if msg_hash in group_hashes:
        # DUPLICATE topildi!
        first_msg_id = group_hashes[msg_hash]["first_message_id"]
        duplicate_count = group_hashes[msg_hash]["count"]

        try:
            # Takroriy xabarni o'chirish
            await bot.delete_message(message.chat.id, message.message_id)

            # Statistikani yangilash
            group_hashes[msg_hash]["count"] += 1
            save_duplicate_cache()

            print(f"[DUPLICATE] Guruh: {message.chat.title or message.chat.id}")
            print(f"  └─ O'chirildi: #{message.message_id}")
            print(f"  └─ Birinchi xabar: #{first_msg_id}")
            print(f"  └─ Jami dublikatlar: {duplicate_count + 1}")

        except Exception as e:
            print(f"[X] Xabar o'chirishda xatolik: {e}")
            # Agar bot admin emas yoki xabar o'chirib bo'lmasa
            if "not enough rights" in str(e).lower() or "message can't be deleted" in str(e).lower():
                print(f"[OGOHLANTIRISH] Bot '{message.chat.title}' guruhda admin emas!")

    else:
        # YANGI xabar - hash'ni saqlash
        group_hashes[msg_hash] = {
            "first_message_id": message.message_id,
            "timestamp": time.time(),
            "count": 0  # Hali dublikat yo'q
        }
        save_duplicate_cache()


# ============================================================
# ADMIN COMMANDS
# ============================================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start buyrug'i - bot haqida ma'lumot"""
    if message.from_user.id not in ADMIN_IDS:
        return

    await message.answer(
        "🤖 <b>Duplicate Remover Bot</b>\n\n"
        "Vazifasi: Target guruhlardagi takroriy xabarlarni avtomatik o'chirish\n\n"
        "Buyruqlar:\n"
        "/stats - Statistika ko'rish\n"
        "/clear - Cache'ni tozalash\n"
        "/cleanup - Eski hashlarni tozalash\n\n"
        "Bot avtomatik ishlaydi, hech narsa qilish kerak emas.",
        parse_mode="HTML"
    )


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Statistika ko'rish"""
    if message.from_user.id not in ADMIN_IDS:
        return

    total_groups = len(message_hashes)
    total_hashes = sum(len(group_hashes) for group_hashes in message_hashes.values())
    total_duplicates = sum(
        sum(hash_data["count"] for hash_data in group_hashes.values())
        for group_hashes in message_hashes.values()
    )

    stats_text = (
        "📊 <b>Duplicate Remover Statistikasi</b>\n\n"
        f"👥 Guruhlar: {total_groups}\n"
        f"🔑 Unikal xabarlar: {total_hashes}\n"
        f"🗑 O'chirilgan dublikatlar: {total_duplicates}\n\n"
    )

    # Har bir guruh uchun detallari
    if message_hashes:
        stats_text += "<b>Guruhlar bo'yicha:</b>\n"
        for group_id, group_hashes in message_hashes.items():
            group_duplicates = sum(hash_data["count"] for hash_data in group_hashes.values())
            stats_text += f"\n• Guruh {group_id}:\n"
            stats_text += f"  └─ Unikal: {len(group_hashes)}, O'chirilgan: {group_duplicates}\n"

    await message.answer(stats_text, parse_mode="HTML")


@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    """Cache'ni to'liq tozalash"""
    if message.from_user.id not in ADMIN_IDS:
        return

    global message_hashes
    old_count = sum(len(group_hashes) for group_hashes in message_hashes.values())

    message_hashes = {}
    save_duplicate_cache()

    await message.answer(
        f"✅ Cache tozalandi\n\n"
        f"O'chirilgan xashlar: {old_count}",
        parse_mode="HTML"
    )


@dp.message(Command("cleanup"))
async def cmd_cleanup(message: types.Message):
    """Eski hashlarni tozalash (24 soatdan eski)"""
    if message.from_user.id not in ADMIN_IDS:
        return

    cleanup_old_hashes()

    await message.answer(
        "✅ Eski hashlar tozalandi\n\n"
        "24 soatdan eski hashlar o'chirildi.",
        parse_mode="HTML"
    )


# ============================================================
# BACKGROUND TASKS
# ============================================================

async def periodic_cleanup():
    """Har 1 soatda eski hashlarni tozalash"""
    while True:
        await asyncio.sleep(3600)  # 1 soat
        cleanup_old_hashes()


# ============================================================
# MAIN FUNCTION
# ============================================================

async def run_duplicate_remover_bot():
    """Duplicate Remover Botni ishga tushirish"""
    print("[START] Duplicate Remover Bot ishga tushmoqda...")

    # Cache'ni yuklash
    load_duplicate_cache()

    # Periodic cleanup task
    asyncio.create_task(periodic_cleanup())

    print("[OK] Duplicate Remover Bot ulandi")
    print("[INFO] Target guruhlardagi takroriy xabarlar avtomatik o'chiriladi")

    # Botni ishga tushirish
    await dp.start_polling(bot)


# ============================================================
# ENTRY POINT (for standalone testing)
# ============================================================

if __name__ == "__main__":
    asyncio.run(run_duplicate_remover_bot())
