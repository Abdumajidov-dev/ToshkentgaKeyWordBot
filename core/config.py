import os
import json

# ============================================================
# TELEGRAM API CREDENTIALS
# ============================================================
# Environment variables yoki default qiymatlar
api_id = int(os.getenv("API_ID", "21318254"))
api_hash = os.getenv("API_HASH", "bd01206ecf54279803192f5a1b33e3ae")

# UserBot uchun alohida credentials
USERBOT_API_ID = int(os.getenv("USERBOT_API_ID", "35590072"))
USERBOT_API_HASH = os.getenv("USERBOT_API_HASH", "48e5dad8bef68a54aac5b2ce0702b82c")

# ============================================================
# BOT TOKENS (BotFather dan oling)
# ============================================================
# Admin Bot - Keywords va Groups bilan ishlash
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "8250455047:AAHfUMysLqgaOmmhRob6cv7h0Y2uVhSnDgM")

# Customer Bot - Mijozlar va to'lovlar bilan ishlash
CUSTOMER_BOT_TOKEN = os.getenv("CUSTOMER_BOT_TOKEN", "8383987517:AAGb68qvvOG04huoFOX6OmTteYOpkS7Clo0")

# Duplicate Remover Bot - Takroriy habarlarni o'chirish
DUPLICATE_REMOVER_TOKEN = os.getenv("DUPLICATE_REMOVER_TOKEN", "8148323755:AAHoHMGEQx8_DQwwwryJqce0GG8Hdo1tHHQ")

# ============================================================
# ADMIN IDS (@userinfobot dan ID olish mumkin)
# ============================================================
# Environment variable dan JSON array sifatida olish
_admin_ids_env = os.getenv("ADMIN_IDS", "[7106025530,5129045986]")
try:
    ADMIN_IDS = json.loads(_admin_ids_env)
except:
    ADMIN_IDS = [7106025530, 5129045986]

# ============================================================
# GURUHLAR
# ============================================================
# Test uchun private guruh
TEST_GROUP_LINK = os.getenv("TEST_GROUP_LINK", "https://t.me/+A3DpeN93ohg3ODgy")
TEST_GROUP_ID = int(os.getenv("TEST_GROUP_ID", "-5002847429"))

# ============================================================
# PATHS
# ============================================================
import pathlib
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
SESSIONS_DIR = PROJECT_ROOT / "sessions"
DATA_DIR = PROJECT_ROOT / "data"

# Ensure directories exist
SESSIONS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# ============================================================
# ESKI QIYMATLAR (backward compatibility)
# ============================================================
BOT_TOKEN = ADMIN_BOT_TOKEN  # Eski kod uchun
ADMIN_ID = 7106025530
session_path = str(SESSIONS_DIR / "userbot_session")
DATA_FILE = "bot_data.json"
BUFFER_GROUP = ""