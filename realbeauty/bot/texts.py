"""
Central Uzbek text + label constants for the bot.

DB `MessageTemplate`s remain the source of truth for campaign copy (welcome,
week1/2, birthday, etc.) and are admin-editable. These constants are the fixed
UI strings (prompts, menu labels, fallbacks) that are not template-driven.
"""

from __future__ import annotations

# --- Main menu (reply keyboard) labels ---
MENU_TUTORIALS = "📚 Qo'llanmalar"
MENU_CATALOG = "🛍 Mahsulotlar"
MENU_FEEDBACK = "⭐️ Mahsulotga baho"
# Customers keep the old reply keyboard until the bot replaces it; the old
# label must keep working or their button silently falls to the fallback.
MENU_FEEDBACK_LEGACY = "💬 Fikr bildirish"
MENU_SUPPORT = "✍️ Savol / Murojaat"
MENU_DISCOUNTS = "🎁 Chegirmalar"
MENU_TIPS = "💡 Maslahatlar"
MENU_PROFILE = "👤 Profil"
MENU_HELP = "ℹ️ Yordam"

# --- Registration prompts ---
GREETING_SELF = (
    "👋 <b>Real Beauty</b>ga xush kelibsiz!\n\n"
    "Ro'yxatdan o'tish uchun to'liq ismingizni yozing."
)
GREETING_ADMIN = (
    "👋 Sizga <b>{admin_name}</b> ro'yxatdan o'tishda yordam beradi.\n\n"
    "Iltimos, to'liq ismingizni yozing."
)
ASK_FULL_NAME = "Iltimos, to'liq ismingizni yozing."
NAME_TOO_SHORT = "Ism juda qisqa. To'liq ismingizni yozing."
NAME_INVALID = "Ismda faqat harflar bo'lsin. Qayta yozing."
ASK_BIRTH_DATE = "📅 Tug'ilgan sanangiz? (kk.oo.yyyy)"
INVALID_DATE = (
    "❌ Sana noto'g'ri. <b>kk.oo.yyyy</b> ko'rinishida yozing (masalan: 25.12.1995)."
)
DATE_IN_FUTURE = "❌ Tug'ilgan sana kelajakda bo'lishi mumkin emas. Qayta yozing."
DATE_TOO_OLD = "❌ Sana juda eski ko'rinadi. Tekshirib, qayta yozing."
ASK_PHONE = "📱 Telefon raqamingiz?"
ASK_PHONE_AGAIN = "Iltimos, telefon raqamingizni yuboring yoki yozing."
INVALID_PHONE = (
    "❌ Raqam noto'g'ri. Masalan: <b>+998 90 123 45 67</b>\n"
    "Yoki pastdagi tugma orqali kontaktingizni ulashing."
)
CONTACT_NOT_YOURS = (
    "❌ Bu boshqa odamning kontakti. O'z raqamingizni yuboring yoki yozing."
)

# --- Returning / blocked users ---
WELCOME_BACK = (
    "👋 Qaytganingizdan xursandmiz, <b>{name}</b>!\n\n"
    "Ma'lumotlaringiz saqlanib qolgan. Menyudan foydalaning 👇"
)
ACCOUNT_DISABLED = (
    "⛔️ Hisobingiz vaqtincha faol emas.\n\n"
    "Savolingiz bo'lsa, do'konimizga murojaat qiling."
)
SHARE_CONTACT = "📱 Kontaktni ulashish"
ASK_FACE_CONDITION = "🧴 Teri turingiz?"
ASK_PHOTO = "📷 Rasmingizni yuboring (ixtiyoriy)."
SKIP = "⏭ O'tkazib yuborish"
REG_SAVED_FALLBACK = "✅ Ro'yxatdan o'tish yakunlandi! Real Beauty'ga xush kelibsiz."
REG_ERROR = "Saqlashda xatolik yuz berdi. Iltimos, /start ni qayta bosing."

# --- Admin notifications ---
ADMIN_USER_STARTED = (
    "🆕 Yangi foydalanuvchi referal havolangiz orqali start bosdi.\n"
    "Telegram ID: <code>{telegram_id}</code>\n"
    "Holat: to'ldirilishi kutilmoqda."
)
ADMIN_USER_REGISTERED = "✅ <b>{full_name}</b> muvaffaqiyatli ro'yxatdan o'tdi."

# --- Tutorials / products ---
PURCHASE_THANKS = (
    "🛍 Xaridingiz uchun rahmat!\n\n"
    "Quyida mahsulotdan qanday foydalanish bo'yicha qo'llanma. "
    "Bir haftadan so'ng natijangizni so'raymiz 😊"
)
NO_PRODUCTS = "Sizda hozircha mahsulotlar yo'q."
TUTORIAL_INTRO_FALLBACK = "📘 <b>{product}</b> uchun qo'llanma"
VIDEO_COMING_SOON = "⏳ Ushbu bosqich uchun video tez orada qo'shiladi."
STEP_NOT_FOUND = "Bosqich topilmadi."

# --- Feedback (rating first — one tap; text after, optional) ---
FEEDBACK_ASK_RATING = "⭐️ Mahsulotni 1 dan 5 gacha baholang:"
FEEDBACK_ASK_TEXT = (
    "💬 Qo'shimcha fikr yozasizmi? (ixtiyoriy)\n\n"
    "Nima yoqdi, nima yoqmadi — yozib qoldiring, "
    "yoki pastdagi tugma bilan o'tkazib yuboring."
)
FEEDBACK_THANKS_FALLBACK = "🙏 Fikringiz uchun rahmat!"
FEEDBACK_SAVE_ERROR = "Fikrni saqlab bo'lmadi. Keyinroq urinib ko'ring."
FEEDBACK_PICK_PRODUCT = "Qaysi mahsulotga baho bermoqchisiz?"

# --- Support (free-form questions) ---
SUPPORT_ASK = (
    "✍️ Savolingiz yoki murojaatingizni yozing.\n\n"
    "Matn yoki rasm yuborishingiz mumkin — jamoamiz shu yerda javob beradi.\n"
    "Menyuga qaytish uchun pastdagi tugmalardan foydalaning."
)
SUPPORT_EMPTY = "Iltimos, matn yozing yoki rasm yuboring."
SUPPORT_SAVED = (
    "✅ Qabul qilindi! Jamoamiz tez orada shu yerda javob beradi.\n\n"
    "Yana yozmoqchi bo'lsangiz — shunchaki davom eting 👇"
)
SUPPORT_SAVE_ERROR = "Murojaatni saqlab bo'lmadi. Keyinroq urinib ko'ring."
SUPPORT_REPLY_BTN = "✍️ Javob yozish"

# --- Fallback (unhandled messages) ---
UNKNOWN_MESSAGE = (
    "Sizni tushunmadim 🤔\n\n"
    "Pastdagi menyudan kerakli bo'limni tanlang. Savolingiz bo'lsa — "
    "«✍️ Savol / Murojaat» tugmasini bosing."
)

# --- Progress (before/after) ---
PROGRESS_ASK_BEFORE = "📷 Avval <b>OLDIN</b> rasmingizni yuboring."
PROGRESS_ASK_AFTER = "📷 Endi <b>KEYIN</b> rasmingizni yuboring."
PROGRESS_NOT_PHOTO = "Iltimos, matn emas, rasm yuboring."
PROGRESS_SAVE_ERROR = "Rasmni saqlab bo'lmadi. Qaytadan urinib ko'ring."
PROGRESS_DONE = "🙏 Rahmat! Jamoamiz natijangizni ko'rib chiqadi."

# --- Discounts ---
NO_DISCOUNTS = "Hozircha faol chegirmalar yo'q."
DISCOUNTS_HEADER = "🎁 <b>Faol chegirmalar:</b>"

# --- Catalog (all active products, not just owned ones) ---
CATALOG_HEADER = "🛍 <b>Bizning mahsulotlar:</b>"
CATALOG_EMPTY = "Katalog hozircha bo'sh. Tez orada to'ldiriladi!"
CATALOG_FOOTER = (
    "📍 Xarid qilish uchun do'konimizga keling yoki "
    "«✍️ Savol / Murojaat» orqali yozing — yordam beramiz."
)

# --- Skin-care tips (the \"beauty assistant\" section) ---
TIPS_GENERIC = (
    "💡 <b>Umumiy parvarish qoidalari</b>\n\n"
    "1️⃣ Ketma-ketlik: tozalash → toner → serum → krem\n"
    "2️⃣ Har kuni ertalab SPF ishlating — bulutli kunda ham\n"
    "3️⃣ Natija 2–4 haftada ko'rinadi — muntazamlik muhim\n"
    "4️⃣ Yangi mahsulotni avval bilak terisida sinab ko'ring\n"
    "5️⃣ Kuniga kamida 1.5–2 litr suv iching\n\n"
    "Teri turingizga mos maslahat olish uchun profilingizda "
    "teri turini to'ldiring."
)
TIPS_BY_SKIN = {
    "dry": (
        "💡 <b>Quruq teri uchun maslahatlar</b>\n\n"
        "• Yumshoq, ko'piksiz tozalovchi vositalar tanlang\n"
        "• Spirtsiz toner ishlating\n"
        "• Namlantiruvchi kremni nam teriga suring — namlikni qulflaydi\n"
        "• Issiq suv bilan yuvmang — iliq suv yetarli\n"
        "• Kechqurun boyroq (qalinroq) krem ishlating\n"
        "• Ertalab SPF — albatta"
    ),
    "oily": (
        "💡 <b>Yog'li teri uchun maslahatlar</b>\n\n"
        "• Penka bilan kuniga 2 marta tozalang — ko'p emas, aks holda "
        "teri yana ko'proq yog' ishlab chiqaradi\n"
        "• Yengil, komedogen bo'lmagan namlantiruvchi tanlang — "
        "yog'li teri ham namlikka muhtoj\n"
        "• Matlashtiruvchi toner foydali\n"
        "• Yuzga qo'l tekkizmaslikka harakat qiling\n"
        "• SPF — yengil, gel formulada"
    ),
    "combined": (
        "💡 <b>Aralash teri uchun maslahatlar</b>\n\n"
        "• T-zona (peshona, burun, iyak) uchun yengil vositalar, "
        "yonoqlarga boyroq krem\n"
        "• Haftada 1 marta yumshoq eksfoliatsiya\n"
        "• Toner butun yuzga, namlantiruvchi zonalarga qarab\n"
        "• Og'ir, yog'li kremlardan saqlaning\n"
        "• Ertalab SPF unutmang"
    ),
    "normal": (
        "💡 <b>Normal teri uchun maslahatlar</b>\n\n"
        "• Muvozanatni saqlang: tozalash → toner → namlantirish\n"
        "• Haftada 1 marta yengil eksfoliatsiya kifoya\n"
        "• Mavsumga qarab kremni almashtiring: qishda boyroq, "
        "yozda yengilroq\n"
        "• Ertalab SPF — teri yoshligini saqlaydi"
    ),
    "sensitive": (
        "💡 <b>Sezgir teri uchun maslahatlar</b>\n\n"
        "• Har yangi mahsulotni avval bilak terisida 24 soat sinang\n"
        "• Atirsiz (fragrance-free) formulalarni tanlang\n"
        "• Skrablardan saqlaning — kimyoviy yumshoq eksfoliantlar ma'qul\n"
        "• Kam vosita — yaxshi: 3-4 bosqichli sodda parvarish\n"
        "• Mineral (fizik) SPF ko'proq mos keladi"
    ),
}
TIPS_FOOTER = (
    "\n\n❓ Savolingiz bo'lsa — «✍️ Savol / Murojaat» tugmasini bosing, "
    "mutaxassislarimiz javob beradi."
)

# --- Profile ---
PROFILE_TEMPLATE = (
    "👤 <b>Profilingiz</b>\n\n"
    "Ism: {full_name}\n"
    "Telefon: {phone}\n"
    "Tug'ilgan sana: {birth_date}\n"
    "Teri turi: {face}\n"
    "Mahsulotlar: {products}"
)
NOT_REGISTERED = "Iltimos, avval /start bosib ro'yxatdan o'ting."

# --- Menu / help ---
MENU_OPENED = "Asosiy menyu. Kerakli bo'limni tanlang 👇"
HELP_TEXT = (
    "ℹ️ <b>Real Beauty bot</b>\n\n"
    "• 📚 Qo'llanmalar — siz olgan mahsulotlarning video darslari\n"
    "• 🛍 Mahsulotlar — do'konimizdagi barcha mahsulotlar katalogi\n"
    "• ⭐️ Mahsulotga baho — olgan mahsulotingizga yulduz va fikr "
    "qoldirasiz (biz sifatni shu orqali kuzatamiz)\n"
    "• ✍️ Savol / Murojaat — jamoamiz bilan jonli yozishma: savol "
    "yozasiz, javob shu yerda keladi\n"
    "• 🎁 Chegirmalar — joriy aksiyalar va promokodlar\n"
    "• 💡 Maslahatlar — teri turingizga mos parvarish maslahatlari\n"
    "• 👤 Profil — ma'lumotlaringiz\n\n"
    "Menyuni ochish uchun /menu buyrug'ini yuboring."
)

# --- Seller ---
SELLER_ONLY = "⛔️ Bu buyruq faqat sotuvchilar uchun."
MY_LINK = "🔗 Sizning referal havolangiz:\n<code>{link}</code>"
