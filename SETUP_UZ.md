# 🚀 Tezkor Telegram Keyword Bot - O'rnatish yo'riqnomasi

## 📋 Tavsif

Bu bot Telegram guruhlaridagi xabarlarni kalit so'zlar bo'yicha kuzatib, topilgan xabarlarni asosiy guruhga yuboradi.

**Asosiy xususiyatlar:**
- ⚡ **FAST rejim** - Admin botli guruhlar uchun (xabar o'chib ketishidan oldin ushlaydi)
- 📝 **NORMAL rejim** - Oddiy guruhlar uchun
- 🚀 **Raw events** - Maksimal tezlik (UpdateNewMessage ni bevosita ushlash)
- 💾 **Cache tizimi** - Guruhlarni xotirada saqlash (tezroq ishlash uchun)
- ⚡ **uvloop** - Event loop optimizatsiyasi (3-5x tezroq)

---

## 🔧 O'rnatish

### 1️⃣ Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

**Windows'da uvloop muammosi bo'lsa:**
uvloop faqat Linux/macOS'da ishlaydi. Windows'da bot avtomatik standart asyncio'ga o'tadi.

---

### 2️⃣ API ma'lumotlarni olish

1. **Telegram API (UserBot uchun):**
   - https://my.telegram.org ga kiring
   - "API development tools" bo'limiga o'ting
   - `api_id` va `api_hash` ni ko'chirib oling

2. **Bot Token (Admin Bot uchun):**
   - Telegram'da @BotFather ni oching
   - `/newbot` buyrug'ini yuboring
   - Bot yaratib, tokenni oling

3. **Admin ID:**
   - @userinfobot ga `/start` yuboring
   - O'z ID ingizni ko'chirib oling

---

### 3️⃣ config.py ni sozlash

```python
api_id = 12345678  # my.telegram.org dan
api_hash = "abcdef123456..."  # my.telegram.org dan

BOT_TOKEN = "123456:ABCdef..."  # @BotFather dan

ADMIN_ID = 1234567890  # @userinfobot dan

BUFFER_GROUP = "-1001234567890"  # FAST guruhlar uchun buffer
```

**MUHIM:** `userbot.py` faylida ham API credentials bor (13-14 qatorlar). Ularni ham o'zgartiring!

---

### 4️⃣ Buffer guruh yaratish (FAST rejim uchun)

1. Telegram'da yangi **private group** yarating
2. Userbot'ni (o'zingizni) guruhga qo'shing
3. Guruh ID sini oling:
   - Guruhga xabar yuboring
   - Bot'ni ishga tushiring: `python main.py`
   - Konsolda guruh ID sini ko'rish mumkin
   - Yoki @username_to_id_bot dan foydalaning

4. Buffer ID ni `bot_data.json` yoki admin bot orqali sozlang

---

## 🎮 Ishlatish

### Bot'ni ishga tushirish

```bash
python main.py
```

Bot ikkita komponentni bir vaqtda ishga tushiradi:
1. **UserBot** - Guruhlarni kuzatadi
2. **Admin Bot** - Sozlamalarni boshqaradi

---

### Admin Bot orqali sozlash

1. Admin bot'ga `/start` yuboring
2. Quyidagi menyular ochiladi:

#### 🔑 Kalit so'zlar
- Qo'shish: kalit so'z kiriting (masalan: "taksi kerak")
- O'chirish: o'chirmoqchi bo'lgan so'zni kiriting

#### 📥 Source guruhlar
- **Qo'shish:**
  1. "Source guruhlar" → "Qo'shish"
  2. Guruh turini tanlang:
     - ⚡ **FAST** - Admin botli guruhlar (xabar tez o'chadi)
     - 📝 **NORMAL** - Oddiy guruhlar
  3. Guruh username yoki ID ni kiriting

- **O'chirish:** Guruh username/ID ni yuboring

#### 📤 Target guruhlar
- Topilgan xabarlar yuborilishi kerak bo'lgan guruh
- ID formatda: `-1001234567890`

#### ⚡ Buffer guruh
- FAST source guruhlar uchun
- Xabar darhol bu yerga forward qilinadi
- Keyin formatlab asosiy target guruhga yuboriladi

#### 📊 Statistika
- Umumiy ma'lumotlar
- Fast/Normal guruhlar soni
- Buffer sozlanganligini ko'rish

---

## ⚡ FAST vs NORMAL rejim

### 📝 NORMAL guruhlar
```
Xabar keldi → Kalit so'z tekshirildi → Formatlab target'ga yuborildi
Vaqt: ~0.5-1 sekund
```

**Ishlatish:** Oddiy guruhlar, admin bot yo'q joylar

---

### ⚡ FAST guruhlar
```
Xabar keldi → DARHOL buffer'ga forward → Orqa fonda formatlanadi → Target'ga yuboriladi
Vaqt: ~0.1-0.3 sekund (forward), formatlab yuborish parallel
```

**Ishlatish:**
- Admin botli guruhlar (xabarni darhol o'chiradi)
- Juda tez xabar o'chib ketadigan joylar
- Boshqa botlar bilan raqobat bo'lsa

**Afzalliklari:**
- Xabarni o'chib ketishidan oldin ushlaydi
- Buffer'ga forward tezroq (formatting'dan tezroq)
- Formatting orqa fonda (async task) ishlaydi

---

## 🔍 Xatoliklarni tuzatish

### Bot ulanmayapti
```bash
python test_connection.py
```

### Flood ban tekshirish
```bash
python check_ban.py
```

### Guruhlar topilmayapti
- UserBot telefon raqami bilan kiring
- Guruhga a'zo bo'lganingizni tekshiring
- 30 daqiqa kuting (auto-update)

### FAST guruhda xabar topilmayapti
- Buffer guruh sozlanganini tekshiring
- UserBot guruhda bo'lishi kerak
- Raw events handler yoniqligini tekshiring (konsol log'lari)

---

## 📁 Fayl tuzilishi

```
ToshkentgaKeyWordBot/
├── main.py              # Asosiy fayl (bot'ni ishga tushirish)
├── userbot.py           # Telethon - guruhlarni kuzatish
├── admin_bot.py         # Aiogram - admin panel
├── storage.py           # Ma'lumotlarni saqlash
├── config.py            # Sozlamalar
├── bot_data.json        # Keywords, source/target guruhlar
├── requirements.txt     # Kutubxonalar
├── test_connection.py   # API test qilish
├── check_ban.py         # Flood ban tekshirish
└── SETUP_UZ.md          # Bu fayl
```

---

## ⚙️ Tizim talablari

- Python 3.8+
- Linux/macOS (uvloop uchun) yoki Windows (standart asyncio)
- Internet tezligi: 1+ Mbps (FAST rejim uchun)

---

## 🆘 Yordam

Muammo bo'lsa:
1. `check_ban.py` ni ishga tushiring
2. `test_connection.py` ni sinab ko'ring
3. Konsol log'larini o'qing (xatolik haqida ma'lumot)
4. `bot_data.json` to'g'riligini tekshiring

---

## 📝 Muhim eslatmalar

1. **UserBot credentials:**
   - `config.py` va `userbot.py` da (13-14 qatorlar) ikki joyda bor
   - Ikkala joyda ham bir xil qiymatlarni kiriting

2. **Buffer guruh:**
   - Faqat FAST source guruhlar uchun kerak
   - Agar FAST guruh yo'q bo'lsa, buffer kerak emas

3. **Auto-update:**
   - Source guruhlar har 30 daqiqada avtomatik yangilanadi
   - Yangi guruhga qo'shilsangiz, 30 daqiqa kuting

4. **Flood wait:**
   - Agar FloodWaitError chiqsa, bir necha soat kuting
   - `check_ban.py` orqali holatni tekshiring

---

**Muvaffaqiyatlar! 🚀**
