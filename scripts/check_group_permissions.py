"""
Target guruhlar huquqlarini tekshirish utility
UserBot'ning guruhda yozish huquqi borligini aniqlaydi
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.types import ChatBannedRights
from core.config import USERBOT_API_ID, USERBOT_API_HASH, session_path
from core.storage import load_state


async def check_group_permissions():
    """Target guruhlarni tekshirish"""
    print("=" * 60)
    print("TARGET GURUHLAR HUQUQLARINI TEKSHIRISH")
    print("=" * 60)

    client = TelegramClient(session_path, USERBOT_API_ID, USERBOT_API_HASH)
    await client.start()

    print("\n[OK] UserBot ulandi\n")

    # Bot state'dan target guruhlarni o'qish
    state = load_state()
    target_groups = state.get("target_groups", [])
    buffer_group = state.get("buffer_group", "")

    if not target_groups and not buffer_group:
        print("[!] Target guruhlar topilmadi!")
        print("    Admin bot orqali target guruhlar qo'shing.")
        await client.disconnect()
        return

    all_groups = []
    if buffer_group:
        all_groups.append(("BUFFER", buffer_group))
    for target in target_groups:
        all_groups.append(("TARGET", target))

    print(f"Tekshirilmoqda: {len(all_groups)} ta guruh\n")
    print("-" * 60)

    for group_type, group_id in all_groups:
        try:
            # Guruhni olish
            entity = await client.get_entity(group_id)

            print(f"\n[{group_type}] {group_id}")
            print(f"  Nomi: {getattr(entity, 'title', 'Noma\'lum')}")
            print(f"  Username: @{entity.username}" if hasattr(entity, 'username') and entity.username else "  Username: [Yo'q]")

            # A'zolik statusini tekshirish
            try:
                me = await client.get_me()
                participant = await client.get_permissions(entity, me)

                print(f"  A'zo: ✓ Ha")
                print(f"  Admin: {'✓ Ha' if participant.is_admin else '✗ Yo\'q'}")

                # Yozish huquqini tekshirish
                if participant.is_admin:
                    print(f"  Yozish huquqi: ✓ Admin (to'liq huquq)")
                elif hasattr(participant, 'banned_rights') and participant.banned_rights:
                    banned_rights = participant.banned_rights
                    if banned_rights.send_messages:
                        print(f"  Yozish huquqi: ✗ TAQIQLANGAN")
                        print(f"    XATOLIK: UserBot guruhda yozish huquqiga ega emas!")
                        print(f"    YECHIM 1: UserBot'ni admin qiling")
                        print(f"    YECHIM 2: Guruh sozlamalarida 'Barcha a'zolar yozishi mumkin' ni yoqing")
                    else:
                        print(f"  Yozish huquqi: ✓ Ruxsat berilgan")
                else:
                    print(f"  Yozish huquqi: ✓ Cheklovlar yo'q")

                # Test xabar yuborishga harakat
                print(f"\n  Test xabar yuborish...")
                test_msg = await client.send_message(
                    entity=entity,
                    message="🧪 Test xabar - UserBot ishlayapti ✓\n\nBu xabar avtomatik ravishda o'chiriladi.",
                )
                print(f"  Test xabar: ✓ MUVAFFAQIYATLI yuborildi (ID: {test_msg.id})")

                # Test xabarni o'chirish
                await asyncio.sleep(2)
                await client.delete_messages(entity, test_msg.id)
                print(f"  Test xabar o'chirildi")

            except Exception as e:
                error_msg = str(e)
                if "user not participant" in error_msg.lower() or "no user has" in error_msg.lower():
                    print(f"  A'zo: ✗ YO'Q")
                    print(f"    XATOLIK: UserBot guruhda a'zo emas!")
                    print(f"    YECHIM: UserBot'ni guruhga qo'shing:")
                    if hasattr(entity, 'username') and entity.username:
                        print(f"    Link: https://t.me/{entity.username}")
                    else:
                        print(f"    Guruh ID: {group_id}")
                elif "can't write" in error_msg.lower() or "chat write forbidden" in error_msg.lower():
                    print(f"  A'zo: ✓ Ha")
                    print(f"  Yozish huquqi: ✗ TAQIQLANGAN")
                    print(f"    XATOLIK: {error_msg}")
                    print(f"    YECHIM 1: UserBot'ni admin qiling")
                    print(f"    YECHIM 2: Guruh sozlamalarida 'Barcha a'zolar yozishi mumkin' ni yoqing")
                elif "flood" in error_msg.lower():
                    print(f"  A'zo: ✓ Ha")
                    print(f"  FloodWait: ✗ Telegram limiti")
                    print(f"    OGOHLANTIRISH: {error_msg}")
                    print(f"    YECHIM: Biroz kutib, qaytadan urinib ko'ring")
                else:
                    print(f"  XATOLIK: {error_msg}")

        except Exception as e:
            print(f"\n[X] {group_type} {group_id}")
            print(f"  Guruhni ochib bo'lmadi: {e}")
            if "no entity" in str(e).lower() or "could not find" in str(e).lower():
                print(f"  YECHIM: Guruh ID to'g'riligini tekshiring yoki UserBot'ni guruhga qo'shing")

        print("-" * 60)

    await client.disconnect()
    print("\n[TUGADI] Tekshiruv yakunlandi")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(check_group_permissions())
