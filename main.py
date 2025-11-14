import asyncio
from userbot import run_userbot
from admin_bot import run_admin_bot

async def main():
    await asyncio.gather(run_userbot(), run_admin_bot())

if __name__ == "__main__":
    asyncio.run(main())
