# Render.com ga Deploy qilish

## 1. Tayorgarlik

### GitHub repositoriyasini yangilash
```bash
git add .
git commit -m "Add Render deployment files"
git push
```

## 2. Render.com da sozlash

### A. Account yaratish
1. https://render.com ga kiring
2. GitHub akkauntingiz bilan sign up qiling

### B. Yangi Web Service yaratish
1. Dashboard → **New** → **Web Service**
2. GitHub repositoriyangizni ulang: `ToshkentgaKeyWordBot`
3. Quyidagi sozlamalarni kiriting:

**Basic Settings:**
- **Name:** `toshkent-keyword-bot`
- **Region:** `Frankfurt (EU Central)` (yoki sizga yaqin region)
- **Branch:** `main`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`

**Instance Type:**
- **Free** (test uchun) yoki **Starter** ($7/month)

### C. Environment Variables qo'shish

**Environment** bo'limida quyidagi o'zgaruvchilarni qo'shing:

```
USERBOT_API_ID=35590072
USERBOT_API_HASH=48e5dad8bef68a54aac5b2ce0702b82c
ADMIN_BOT_TOKEN=8250455047:AAHfUMysLqgaOmmhRob6cv7h0Y2uVhSnDgM
CUSTOMER_BOT_TOKEN=8383987517:AAGb68qvvOG04huoFOX6OmTteYOpkS7Clo0
TEST_GROUP_LINK=https://t.me/+A3DpeN93ohg3ODgy
TEST_GROUP_ID=-5002847429
```

**Admin IDs (JSON format):**
```
ADMIN_IDS=[7106025530,5129045986]
```

**Python Version:**
```
PYTHON_VERSION=3.11.0
```

## 3. Session faylini yuklash

### Muhim!
Render serverda session yaratish qiyin, shuning uchun:

1. Local kompyuterda `sessions/userbot_session.session` faylini GitHub'ga yuklang (faqat deploy uchun)
2. Yoki Render Shell orqali session yarating

**Varaint 1: GitHub orqali (oson)**

`.gitignore` dan session'ni vaqtinchalik olib tashlang:
```bash
# .gitignore faylida *.session qatorini comment qiling
# *.session

git add sessions/userbot_session.session
git commit -m "Add session for deployment"
git push
```

**⚠️ XAVFSIZLIK:** Deploy qilgandan keyin yana `.gitignore` ga qaytaring!

**Variant 2: Render Shell orqali**

Render dashboard → **Shell** → quyidagi buyruqni bajaring:
```bash
python -m scripts.test_connection
```

## 4. Deploy qilish

1. **Create Web Service** tugmasini bosing
2. Render avtomatik build qiladi va deploy qiladi
3. Logs'ni kuzating: **Logs** bo'limida

## 5. Tekshirish

Deploy muvaffaqiyatli bo'lsa, logs'da ko'rasiz:
```
============================================================
TOSHKENT KEYWORD BOT - 3 BOT SYSTEM
============================================================

Botlar ishga tushmoqda...
1. UserBot - Keyword monitoring (FAST/NORMAL)
2. Admin Bot - Keywords va Groups
3. Customer Bot - Mijozlar va to'lovlar

============================================================

[OK] UserBot ulandi
[OK] Admin Bot ishga tushdi
[OK] Customer Bot ishga tushdi
```

## 6. Monitoring

### Logs ko'rish
Render dashboard → **Logs**

### Botni restart qilish
Render dashboard → **Manual Deploy** → **Deploy latest commit**

## 7. Xavfsizlik

### Keyin qilish kerak:
1. Session faylini GitHub'dan o'chirish:
```bash
git rm --cached sessions/userbot_session.session
git commit -m "Remove session from git"
git push
```

2. `.gitignore`ni qayta tiklash:
```bash
# .gitignore da uncomment qiling
*.session
*.session-journal
```

## 8. Muammolarni hal qilish

### "Session not found" xatosi
- Render Shell orqali session yarating
- Yoki local session'ni yuklang (yuqoridagi ko'rsatma)

### "Module not found" xatosi
- `requirements.txt` to'g'riligini tekshiring
- Render'da build logs'ni ko'ring

### Bot javob bermayapti
- Render logs'da xatoliklarni qidiring
- Environment variables to'g'riligini tekshiring

## 9. Free tier cheklovlar

Render Free tier:
- ✅ 750 soat/oy (31 kun * 24 soat = 744 soat)
- ❌ 15 daqiqa faoliyatsizlikdan keyin o'chadi
- ❌ Restart qilish 30 soniya oladi

**Tavsiya:** Production uchun **Starter** plan ($7/month):
- ✅ 24/7 ishlaydi
- ✅ Tezroq
- ✅ Auto-restart
- ✅ More resources

## 10. Qo'shimcha sozlamalar

### Health Check (ixtiyoriy)
Agar bot HTTP endpoint qo'shsangiz:
- **Health Check Path:** `/health`
- **Health Check Period:** `60` seconds

### Auto-Deploy
Render avtomatik deploy qiladi har safar GitHub'ga push qilganingizda.

**O'chirish uchun:**
Settings → **Auto-Deploy** → `Disabled`

---

**Render Dashboard:** https://dashboard.render.com
**Support:** https://render.com/docs
