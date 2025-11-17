"""
User Cache - FAST guruhlar uchun user ma'lumotlarini saqlash
Xabar o'chirilgandan keyin ham user ma'lumotlarini topish imkonini beradi
"""
import json
import os
from datetime import datetime


USER_CACHE_FILE = "data/user_cache.json"


def load_user_cache():
    """User cache'ni yuklash"""
    if not os.path.exists(USER_CACHE_FILE):
        return {}

    try:
        with open(USER_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[OGOHLANTIRISH] User cache yuklanmadi: {e}")
        return {}


def save_user_cache(cache):
    """User cache'ni saqlash"""
    try:
        os.makedirs(os.path.dirname(USER_CACHE_FILE), exist_ok=True)
        with open(USER_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[OGOHLANTIRISH] User cache saqlanmadi: {e}")


def add_user_to_cache(user_id, user_data):
    """
    Bitta userni cache'ga qo'shish

    Args:
        user_id: User ID (int yoki str)
        user_data: User ma'lumotlari (dict)
    """
    cache = load_user_cache()

    user_id_str = str(user_id)

    # Yangi ma'lumotlarni qo'shish
    cache[user_id_str] = {
        **user_data,
        "cached_at": datetime.now().isoformat()
    }

    save_user_cache(cache)


def add_users_bulk(users_dict):
    """
    Ko'p userlarni bir vaqtda qo'shish

    Args:
        users_dict: {user_id: user_data, ...}
    """
    cache = load_user_cache()

    for user_id, user_data in users_dict.items():
        user_id_str = str(user_id)
        cache[user_id_str] = {
            **user_data,
            "cached_at": datetime.now().isoformat()
        }

    save_user_cache(cache)
    print(f"[OK] {len(users_dict)} ta user cache'ga qo'shildi")


def get_user_from_cache(user_id):
    """
    User ma'lumotlarini cache'dan olish

    Args:
        user_id: User ID (int yoki str)

    Returns:
        User ma'lumotlari (dict) yoki None
    """
    cache = load_user_cache()
    user_id_str = str(user_id)

    return cache.get(user_id_str)


def get_user_display_info(user_id):
    """
    User ma'lumotlarini formatlangan ko'rinishda olish

    Args:
        user_id: User ID (int yoki str)

    Returns:
        Formatlangan string (misol: "@username" yoki "[TEL] +998901234567" yoki "Anvar Karimov")
    """
    user_data = get_user_from_cache(user_id)

    if not user_data:
        return None

    # 1-prioritet: Username
    if user_data.get('username'):
        return user_data['username']

    # 2-prioritet: Telefon
    if user_data.get('phone'):
        return f"[TEL] {user_data['phone']}"

    # 3-prioritet: To'liq ism
    if user_data.get('full_name') and user_data['full_name'] != 'Noma\'lum':
        return user_data['full_name']

    # 4-prioritet: First name
    if user_data.get('first_name'):
        return user_data['first_name']

    return None


def get_cache_stats():
    """Cache statistikasi"""
    cache = load_user_cache()

    total = len(cache)
    with_username = sum(1 for u in cache.values() if u.get('username'))
    with_phone = sum(1 for u in cache.values() if u.get('phone'))

    return {
        'total': total,
        'with_username': with_username,
        'with_phone': with_phone
    }


def clear_old_cache(days=30):
    """
    Eski cache'ni tozalash (days kundan eski)

    Args:
        days: Necha kundan eski cache'ni o'chirish
    """
    from datetime import datetime, timedelta

    cache = load_user_cache()
    cutoff_date = datetime.now() - timedelta(days=days)

    new_cache = {}
    removed_count = 0

    for user_id, user_data in cache.items():
        cached_at = user_data.get('cached_at')
        if cached_at:
            try:
                cached_date = datetime.fromisoformat(cached_at)
                if cached_date >= cutoff_date:
                    new_cache[user_id] = user_data
                else:
                    removed_count += 1
            except:
                # Noto'g'ri format bo'lsa, saqlab qolish
                new_cache[user_id] = user_data
        else:
            # cached_at yo'q bo'lsa, saqlab qolish
            new_cache[user_id] = user_data

    save_user_cache(new_cache)
    print(f"[OK] {removed_count} ta eski cache o'chirildi (>{days} kun)")

    return removed_count
