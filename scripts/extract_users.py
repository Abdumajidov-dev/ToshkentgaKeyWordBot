"""
Source guruhdagi userlarni olish va eksport qilish
UserBot orqali guruh a'zolarining ma'lumotlarini to'plash
"""
import asyncio
import json
import csv
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from core.config import USERBOT_API_ID, USERBOT_API_HASH, session_path
from core.storage import load_state


async def extract_users_from_group(group_id, limit=None, export_format='json'):
    """
    Guruhdan userlarni olish

    Args:
        group_id: Guruh ID yoki username
        limit: Maksimal user soni (None = hammasi)
        export_format: 'json', 'csv', yoki 'both'
    """
    print("=" * 60)
    print("SOURCE GURUH USERLARINI OLISH")
    print("=" * 60)

    client = TelegramClient(session_path, USERBOT_API_ID, USERBOT_API_HASH)
    await client.start()

    print(f"\n[OK] UserBot ulandi")
    print(f"[INFO] Guruh: {group_id}")
    print(f"[INFO] Limit: {limit if limit else 'Cheksiz (hammasi)'}\n")

    try:
        # Guruhni olish
        entity = await client.get_entity(group_id)
        print(f"[OK] Guruh topildi: {getattr(entity, 'title', 'Noma\'lum')}")

        # A'zolarni to'plash
        users_data = []
        offset = 0
        batch_size = 200  # Telegram har safar max 200 ta user beradi

        print(f"\n[JARAYON] Userlar yuklanmoqda...\n")

        while True:
            try:
                # A'zolarni olish
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
                    # Bot'larni o'tkazib yuborish (agar kerak bo'lsa)
                    # if user.bot:
                    #     continue

                    user_info = {
                        'id': user.id,
                        'first_name': user.first_name or '',
                        'last_name': user.last_name or '',
                        'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                        'username': f"@{user.username}" if user.username else None,
                        'phone': f"+{user.phone}" if user.phone else None,
                        'is_bot': user.bot,
                        'is_verified': getattr(user, 'verified', False),
                        'is_premium': getattr(user, 'premium', False),
                        'status': str(user.status.__class__.__name__) if user.status else None,
                    }

                    users_data.append(user_info)

                    # Progress ko'rsatish
                    if len(users_data) % 100 == 0:
                        print(f"  ✓ {len(users_data)} ta user yuklandi...")

                    # Limit tekshirish
                    if limit and len(users_data) >= limit:
                        break

                # Limit yetgan bo'lsa, to'xtatish
                if limit and len(users_data) >= limit:
                    break

                # Keyingi batch
                offset += len(participants.users)

                # Agar yangi userlar yo'q bo'lsa, to'xtatish
                if len(participants.users) < batch_size:
                    break

            except Exception as e:
                print(f"\n[OGOHLANTIRISH] Batch yuklashda xatolik (offset={offset}): {e}")
                break

        print(f"\n[OK] Jami {len(users_data)} ta user toplandi")

        # Eksport qilish
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        group_name = getattr(entity, 'title', str(group_id)).replace(' ', '_')[:30]

        # JSON eksport
        if export_format in ['json', 'both']:
            json_file = f"data/users_{group_name}_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'group_id': str(entity.id),
                    'group_name': getattr(entity, 'title', 'Noma\'lum'),
                    'extracted_at': datetime.now().isoformat(),
                    'total_users': len(users_data),
                    'users': users_data
                }, f, ensure_ascii=False, indent=2)
            print(f"\n[SAQLANDI] JSON: {json_file}")

        # CSV eksport
        if export_format in ['csv', 'both']:
            csv_file = f"data/users_{group_name}_{timestamp}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                if users_data:
                    writer = csv.DictWriter(f, fieldnames=users_data[0].keys())
                    writer.writeheader()
                    writer.writerows(users_data)
            print(f"[SAQLANDI] CSV: {csv_file}")

        # Statistika
        print(f"\n{'=' * 60}")
        print("STATISTIKA")
        print(f"{'=' * 60}")
        print(f"Jami userlar: {len(users_data)}")
        print(f"Username bor: {sum(1 for u in users_data if u['username'])}")
        print(f"Telefon bor: {sum(1 for u in users_data if u['phone'])}")
        print(f"Bot'lar: {sum(1 for u in users_data if u['is_bot'])}")
        print(f"Verified: {sum(1 for u in users_data if u['is_verified'])}")
        print(f"Premium: {sum(1 for u in users_data if u['is_premium'])}")
        print(f"{'=' * 60}\n")

    except Exception as e:
        print(f"\n[X] XATOLIK: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()
        print("[TUGADI] UserBot uzildi")


async def extract_from_all_source_groups():
    """Barcha source guruhlardan userlarni olish"""
    state = load_state()
    source_groups = state.get("source_groups", [])

    if not source_groups:
        print("[!] Source guruhlar topilmadi!")
        print("    Admin bot orqali source guruhlar qo'shing.")
        return

    print("=" * 60)
    print("BARCHA SOURCE GURUHLARDAN USERLARNI OLISH")
    print("=" * 60)
    print(f"\nJami {len(source_groups)} ta source guruh topildi\n")

    for i, group in enumerate(source_groups, 1):
        if isinstance(group, dict):
            group_id = group.get("id")
            group_type = group.get("type", "normal")
        else:
            group_id = group
            group_type = "normal"

        print(f"\n[{i}/{len(source_groups)}] {group_id} ({group_type})")
        print("-" * 60)

        await extract_users_from_group(group_id, limit=None, export_format='json')

        # Rate limiting uchun biroz kutish
        await asyncio.sleep(2)

    print("\n" + "=" * 60)
    print("BARCHA GURUHLAR QAYTA ISHLANDI")
    print("=" * 60)


async def main():
    """Asosiy menyu"""
    print("\n" + "=" * 60)
    print("SOURCE GURUH USERLARINI EKSPORT QILISH")
    print("=" * 60)
    print("\n1. Bitta guruhdan userlarni olish")
    print("2. Barcha source guruhlardan userlarni olish")
    print("3. Ma'lum guruh ID bo'yicha olish")
    print("\nTanlang (1-3): ", end='')

    # Avtomatik tanlash uchun (script ishga tushganda)
    # Default: Barcha source guruhlardan
    choice = input().strip()

    if choice == '1':
        state = load_state()
        source_groups = state.get("source_groups", [])

        if not source_groups:
            print("\n[!] Source guruhlar topilmadi!")
            return

        print("\nMavjud source guruhlar:")
        for i, group in enumerate(source_groups, 1):
            if isinstance(group, dict):
                print(f"  {i}. {group.get('id')} ({group.get('type', 'normal')})")
            else:
                print(f"  {i}. {group}")

        print(f"\nGuruh raqamini tanlang (1-{len(source_groups)}): ", end='')
        idx = int(input().strip()) - 1

        if 0 <= idx < len(source_groups):
            group = source_groups[idx]
            group_id = group.get("id") if isinstance(group, dict) else group

            print("\nLimit (Enter = hammasi): ", end='')
            limit_input = input().strip()
            limit = int(limit_input) if limit_input else None

            print("\nFormat (json/csv/both) [json]: ", end='')
            fmt = input().strip() or 'json'

            await extract_users_from_group(group_id, limit, fmt)
        else:
            print("[!] Noto'g'ri tanlov!")

    elif choice == '2':
        await extract_from_all_source_groups()

    elif choice == '3':
        print("\nGuruh ID yoki username: ", end='')
        group_id = input().strip()

        print("Limit (Enter = hammasi): ", end='')
        limit_input = input().strip()
        limit = int(limit_input) if limit_input else None

        print("Format (json/csv/both) [json]: ", end='')
        fmt = input().strip() or 'json'

        await extract_users_from_group(group_id, limit, fmt)

    else:
        print("[!] Noto'g'ri tanlov!")


if __name__ == "__main__":
    asyncio.run(main())
