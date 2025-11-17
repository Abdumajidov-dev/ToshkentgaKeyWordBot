"""
FAST guruhlardan userlarni cache'ga yuklash - STANDALONE SCRIPT

OGOHLANTIRISH: Bu script faqat UserBot ISHLAMAYOTGANDA ishlatiladi!
Agar UserBot ishlayotgan bo'lsa, "database is locked" xatolik chiqadi.

TAVSIYA: UserBot avtomatik ravishda cache'ni yuklaydi, bu scriptni ishlatish shart emas.
"""
import asyncio
import os
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from core.config import USERBOT_API_ID, USERBOT_API_HASH, session_path
from core.storage import load_state
from core.user_cache import add_users_bulk, get_cache_stats


async def cache_users_from_fast_groups():
    """Barcha FAST guruhlardan userlarni cache'ga yuklash"""
    print("=" * 60)
    print("FAST GURUHLAR USERLARINI CACHE'GA YUKLASH (STANDALONE)")
    print("=" * 60)
    print("\nOGOHLANTIRISH: UserBot ishlamayotganligini tekshiring!")
    print("Agar UserBot ishlasa, 'database is locked' xatolik chiqadi.\n")

    # Session file lock tekshirish
    session_lock = session_path + "-journal"
    if os.path.exists(session_lock):
        print(f"[X] XATOLIK: Session fayl ishlatilmoqda!")
        print(f"    UserBot yoki boshqa Telegram client ishlab turibdi.")
        print(f"    Iltimos, avval UserBot'ni to'xtating.\n")
        return

    client = TelegramClient(session_path, USERBOT_API_ID, USERBOT_API_HASH)

    try:
        await client.start()
        print("\n[OK] UserBot ulandi")

        # FAST guruhlarni olish
        state = load_state()
        source_groups = state.get("source_groups", [])

        fast_groups = []
        for group in source_groups:
            if isinstance(group, dict):
                if group.get("type") == "fast":
                    fast_groups.append(group.get("id"))
            # Eski format (string) bo'lsa, o'tkazib yuborish

        if not fast_groups:
            print("\n[INFO] FAST guruhlar topilmadi")
            print("       Admin bot orqali FAST guruhlar qo'shing")
            return

        print(f"\n[INFO] {len(fast_groups)} ta FAST guruh topildi")
        print("-" * 60)

        all_users = {}

        for i, group_id in enumerate(fast_groups, 1):
            print(f"\n[{i}/{len(fast_groups)}] {group_id}")

            try:
                # Guruhni olish
                entity = await client.get_entity(group_id)
                group_title = getattr(entity, 'title', 'Noma\'lum')
                print(f"  Nomi: {group_title}")

                # Userlarni olish
                offset = 0
                batch_size = 200
                group_user_count = 0

                while True:
                    try:
                        participants = await client(GetParticipantsRequest(
                            channel=entity,
                            filter=ChannelParticipantsSearch(''),
                            offset=offset,
                            limit=batch_size,
                            hash=0
                        ))

                        if not participants.users:
                            break

                        # Har bir userni qayta ishlash
                        for user in participants.users:
                            # Bot'larni o'tkazib yuborish
                            if user.bot:
                                continue

                            user_id = str(user.id)

                            # Agar user allaqachon cache'da bo'lsa, yangilash
                            user_data = {
                                'id': user.id,
                                'first_name': user.first_name or '',
                                'last_name': user.last_name or '',
                                'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or 'Noma\'lum',
                                'username': f"@{user.username}" if user.username else None,
                                'phone': f"+{user.phone}" if user.phone else None,
                                'is_verified': getattr(user, 'verified', False),
                                'is_premium': getattr(user, 'premium', False),
                            }

                            all_users[user_id] = user_data
                            group_user_count += 1

                        # Keyingi batch
                        offset += len(participants.users)

                        # Agar yangi userlar yo'q bo'lsa, to'xtatish
                        if len(participants.users) < batch_size:
                            break

                    except Exception as e:
                        print(f"  [OGOHLANTIRISH] Batch xatolik (offset={offset}): {e}")
                        break

                print(f"  ✓ {group_user_count} ta user cache'ga qo'shildi")

            except Exception as e:
                print(f"  [X] Guruh xatolik: {e}")

            # Rate limiting
            await asyncio.sleep(1)

        # Barcha userlarni bir vaqtda saqlash
        if all_users:
            print(f"\n{'-' * 60}")
            print(f"[SAQLASH] {len(all_users)} ta user cache'ga yozilmoqda...")
            add_users_bulk(all_users)

            # Statistika
            stats = get_cache_stats()
            print(f"\n{'=' * 60}")
            print("CACHE STATISTIKASI")
            print(f"{'=' * 60}")
            print(f"Jami userlar: {stats['total']}")
            print(f"Username bor: {stats['with_username']}")
            print(f"Telefon bor: {stats['with_phone']}")
            print(f"{'=' * 60}\n")
        else:
            print("\n[INFO] Cache'ga qo'shiladigan userlar topilmadi")

    except Exception as e:
        print(f"\n[X] XATOLIK: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()
        print("[TUGADI] UserBot uzildi")


if __name__ == "__main__":
    asyncio.run(cache_users_from_fast_groups())
