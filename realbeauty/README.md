# Real Beauty — Telegram Marketing Bot + CRM

Telegram bot (aiogram 3) + Django 5 admin panel (django-unfold), bitta PostgreSQL
bazada. Celery rejalashtirilgan xabarlarni yuboradi: 1-hafta fikr so'rovi,
2-hafta natija rasmi, tug'ilgan kun chegirmasi.

## Arxitektura

| Qism          | Stack                    | Kirish nuqtasi             |
| ------------- | ------------------------ | -------------------------- |
| Bot           | aiogram 3 + Redis FSM    | `python -m bot.main`       |
| Admin panel   | Django 5 + django-unfold | `gunicorn core.wsgi`       |
| Rejalashtiruv | Celery worker + beat     | `celery -A tasks.celery`   |
| Baza          | PostgreSQL 16            | —                          |
| Broker / FSM  | Redis 7                  | —                          |
| Prod kirish   | nginx (media + proxy)    | `docker/nginx/`            |

### Django app'lar

- `apps.users` — Xaridorlar (`TelegramUser`), sotib olingan mahsulotlar,
  Xodimlar (auth `User` proxy) va sotuvchi profillari (referal havola).
- `apps.products` — Mahsulotlar va qo'llanma qadamlari (himoyalangan video).
- `apps.campaigns` — Xabar shablonlari (har turdan bittadan, Jinja2),
  yuborilganlar jurnali.
- `apps.support` — Murojaatlar: bot ↔ admin ikki tomonlama chat.
- `apps.analytics` — Fikrlar (baho 1-5) va natija rasmlari (original
  Telegramda `file_id` orqali, diskda faqat thumbnail).
- `apps.bot_settings` — Umumiy sozlamalar (singleton) va chegirmalar.

### Muhim dizayn qarorlari

- **Xaridor qo'shish:** faqat ism + telefon. Mijoz botga kirib raqamini
  yuborganda kartasi telefonning oxirgi 9 raqami (`phone_tail`) orqali avtomatik
  ulanadi. Telegram ID hech qayerda qo'lda kiritilmaydi.
- **Rasmlar:** original Telegram serverida qoladi (`file_id`), diskda 400px
  thumbnail (~40KB). Eski thumbnaillar 180 kundan keyin tozalanadi — original
  baribir ochiladi (`/tg-file/<file_id>/` staff-only proxy).
- **Jurnal tozalash:** CampaignLog 90 kun, admin log 90 kun, thumbnail 180 kun —
  haftalik Celery beat.
- **Tarjima:** Django'ning `uz` katalogi chala; yetishmagani `locale/`da.
  `.po` o'zgartirilsa `python scripts/compile_messages.py` yuritiladi
  (gettext talab qilinmaydi).

## Lokal ishga tushirish

```bash
./run_local.sh          # hammasi: db, redis, migrate, django, bot, celery
SEED=1 ./run_local.sh   # + demo ma'lumotlar
```

Admin: http://localhost:8000/admin/ (admin/admin).
Skript eski bot nusxalarini o'zi o'ldiradi — Telegram bitta tokenga bitta
polling ulanishiga ruxsat beradi, ikkinchi nusxa botni "o'lik" qilib qo'yadi.

## Deploy (VPS, Docker)

1. **Server:** Docker + docker compose o'rnatilgan bo'lsin. DNS A-yozuv
   domeningizni serverga qaratsin.

2. **Sozlash:**

   ```bash
   git clone <repo> && cd realbeauty
   cp .env.example .env
   nano .env    # hamma qiymatni to'ldiring — fayl ichida yo'riqnoma bor
   ```

   Majburiy: `DJANGO_SECRET_KEY` (kuchli), `ALLOWED_HOSTS` (domen),
   `POSTGRES_PASSWORD` (kuchli), `BOT_TOKEN`, `BOT_USERNAME`.
   `prod.py` bo'sh/zaif qiymat bilan ataylab ishga tushmaydi.

3. **Ishga tushirish:**

   ```bash
   docker compose up -d --build
   docker compose exec django python manage.py createsuperuser
   ```

   `migrate` servisi avtomatik: baza tayyor bo'lmaguncha app'lar ko'tarilmaydi.

4. **HTTPS:** `certbot --nginx` (yoki Cloudflare proxy). `prod.py`da
   `SECURE_SSL_REDIRECT=True` — TLS'siz ishlamaydi, bu ataylab.

5. **Yangilash:**

   ```bash
   git pull && docker compose up -d --build
   ```

### Diqqat — bitta bot qoidasi

Bitta `BOT_TOKEN` bilan faqat **bitta** bot jarayoni polling qilishi mumkin.
Serverda ishlayotganda lokalda `run_local.sh` ishlatmang (yoki alohida
test-bot token oling), aks holda ikkalasi ham `TelegramConflictError` bilan
talashib, foydalanuvchiga bot o'lik ko'rinadi.

### Zaxira nusxa

```bash
docker compose exec db pg_dump -U realbeauty realbeauty | gzip > backup_$(date +%F).sql.gz
```

Media (thumbnail'lar) `media` volume'da; originallar Telegramda — bazani
saqlasangiz rasmlarga havolalar ham saqlanadi. Cron'ga qo'ying.

## Rollar

| Rol           | Ko'radi                                                        |
| ------------- | -------------------------------------------------------------- |
| Administrator | Hammasi                                                         |
| Sotuvchi      | Xaridorlar (qo'shish/tahrirlash), Murojaatlar (javob), Fikrlar, Natija rasmlari, Mahsulotlar (ko'rish) |

Sotuvchi ruxsatlari kodda: `apps/users/roles.py` (`SELLER_PERMISSIONS`) —
migratsiya 0009 mavjud bazani shu ro'yxatga tenglashtiradi.
