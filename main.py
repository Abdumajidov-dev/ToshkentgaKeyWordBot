"""
Toshkent Keyword Bot - Main Entry Point
Professional Telegram bot system

4 ta bot:
1. UserBot - Keyword monitoring (FAST/NORMAL modes)
2. Admin Bot - Keywords va guruhlar bilan ishlash
3. Customer Bot - Mijozlar va to'lovlar
4. Duplicate Remover Bot - Takroriy habarlarni o'chirish

Author: Abdumajid
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import bots
from bots.userbot import run_userbot
from bots.admin import run_admin_bot
from bots.customer.main import run_customer_bot
from bots.duplicate_remover import run_duplicate_remover_bot

async def main():
    """
    Asosiy funksiya - Barcha 4 ta botni birga ishga tushiradi

    1. UserBot - Keyword monitoring
    2. Admin Bot - Configuration panel
    3. Customer Bot - Payment & subscriptions
    4. Duplicate Remover Bot - Duplicate message removal
    """
    print("="*60)
    print("TOSHKENT KEYWORD BOT - 4 BOT SYSTEM")
    print("="*60)
    print()
    print("Botlar ishga tushmoqda...")
    print("1. UserBot - Keyword monitoring (FAST/NORMAL)")
    print("2. Admin Bot - Keywords va Groups")
    print("3. Customer Bot - Mijozlar va to'lovlar")
    print("4. Duplicate Remover Bot - Takroriy habarlar")
    print()
    print("="*60)
    print()

    try:
        # 4 ta botni birga ishga tushirish
        await asyncio.gather(
            run_userbot(),
            run_admin_bot(),
            run_customer_bot(),
            run_duplicate_remover_bot()
        )
    except KeyboardInterrupt:
        print("\n\nBotlar to'xtatildi")
    except Exception as e:
        print(f"\nXato: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
