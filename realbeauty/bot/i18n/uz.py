"""Uzbek strings — the reference catalogue every other language mirrors."""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # ------------------------------------------------------------------ menu
    "menu.ingredients": "🧪 Qaysi tarkiblarni o'rganamiz",
    "menu.catalog": "🛍 Mahsulotlar",
    "menu.top": "🔥 Bu oydagi top mahsulotlar",
    "menu.feedback": "⭐️ Mahsulotga baho",
    "menu.support": "✍️ Savol / Murojaat",
    "menu.discounts": "🎁 Chegirmalar",
    "menu.bonus": "💎 Bonuslarim",
    "menu.profile": "👤 Profil",
    "menu.help": "ℹ️ Yordam",
    # Customers keep whatever keyboard was on screen the last time they wrote,
    # so labels we have already shipped must keep matching after a rename.
    "menu.legacy_tutorials": "📚 Qo'llanmalar",
    "menu.legacy_feedback": "💬 Fikr bildirish",
    "menu.legacy_tips": "💡 Maslahatlar",
    "menu.opened": "Asosiy menyu. Kerakli bo'limni tanlang 👇",
    # -------------------------------------------------------------- language
    "lang.choose": (
        "🌐 <b>Tilni tanlang / Выберите язык / Choose a language</b>\n\n"
        "Botning barcha xabarlari va tugmalari shu tilda bo'ladi."
    ),
    "lang.changed": "✅ Til o'zgartirildi. Menyudan foydalaning 👇",
    "lang.button": "🌐 Tilni o'zgartirish",
    # ---------------------------------------------------------- registration
    "reg.greeting_self": (
        "👋 <b>Real Beauty</b>ga xush kelibsiz!\n\n"
        "Ro'yxatdan o'tish uchun to'liq ismingizni yozing."
    ),
    "reg.greeting_admin": (
        "👋 Sizga <b>{admin_name}</b> ro'yxatdan o'tishda yordam beradi.\n\n"
        "Iltimos, to'liq ismingizni yozing."
    ),
    "reg.ask_name": "Iltimos, to'liq ismingizni yozing.",
    "reg.name_short": "Ism juda qisqa. To'liq ismingizni yozing.",
    "reg.name_invalid": "Ismda faqat harflar bo'lsin. Qayta yozing.",
    "reg.ask_birth": "📅 Tug'ilgan sanangiz? (kk.oo.yyyy)",
    "reg.invalid_date": (
        "❌ Sana noto'g'ri. <b>kk.oo.yyyy</b> ko'rinishida yozing "
        "(masalan: 25.12.1995)."
    ),
    "reg.date_future": "❌ Tug'ilgan sana kelajakda bo'lishi mumkin emas. Qayta yozing.",
    "reg.date_old": "❌ Sana juda eski ko'rinadi. Tekshirib, qayta yozing.",
    "reg.ask_phone": "📱 Telefon raqamingiz?",
    "reg.ask_phone_again": "Iltimos, telefon raqamingizni yuboring yoki yozing.",
    "reg.invalid_phone": (
        "❌ Raqam noto'g'ri. Masalan: <b>+998 90 123 45 67</b>\n"
        "Yoki pastdagi tugma orqali kontaktingizni ulashing."
    ),
    "reg.contact_not_yours": (
        "❌ Bu boshqa odamning kontakti. O'z raqamingizni yuboring yoki yozing."
    ),
    "reg.share_contact": "📱 Kontaktni ulashish",
    "reg.ask_photo": "📷 Rasmingizni yuboring (ixtiyoriy).",
    "reg.skip": "⏭ O'tkazib yuborish",
    "reg.saved_fallback": (
        "✅ Ro'yxatdan o'tish yakunlandi! Real Beauty'ga xush kelibsiz."
    ),
    "reg.error": "Saqlashda xatolik yuz berdi. Iltimos, /start ni qayta bosing.",
    "reg.invalid_ref": "Referal havola yaroqsiz. O'zingiz ro'yxatdan o'tishingiz mumkin.",
    # -------------------------------------------------------------- account
    "user.welcome_back": (
        "👋 Qaytganingizdan xursandmiz, <b>{name}</b>!\n\n"
        "Ma'lumotlaringiz saqlanib qolgan. Menyudan foydalaning 👇"
    ),
    "user.disabled": (
        "⛔️ Hisobingiz vaqtincha faol emas.\n\n"
        "Savolingiz bo'lsa, do'konimizga murojaat qiling."
    ),
    "user.not_registered": "Iltimos, avval /start bosib ro'yxatdan o'ting.",
    # ----------------------------------------------------------- skin / quiz
    "skin.know_question": (
        "🧴 <b>Yuz turingizni bilasizmi?</b>\n\n"
        "Bilsangiz — darrov tanlaymiz. Bilmasangiz — 10 ta qisqa savol bilan "
        "birga aniqlaymiz, atigi 1 daqiqa vaqt oladi."
    ),
    "skin.know_yes": "✅ Ha, bilaman",
    "skin.know_no": "🔍 Yo'q, aniqlab beringlar",
    "skin.pick": "Teri turingizni tanlang 👇",
    "skin.type.dry": "Quruq",
    "skin.type.oily": "Yog'li",
    "skin.type.combined": "Aralash",
    "skin.type.normal": "Normal",
    "skin.type.sensitive": "Sezgir",
    "quiz.intro": (
        "🔍 <b>Yuzingizni aniqlaymiz</b>\n\n"
        "Sizga 10 ta oddiy savol beramiz. Har biriga <b>0 dan 5 gacha</b> "
        "baho berasiz — 0 «umuman yo'q», 5 «juda ko'p» degani.\n\n"
        "Oxirida teri turingiz va aynan sizga mos parvarish rejasi chiqadi. "
        "Tayyormisiz?"
    ),
    "quiz.start": "🚀 Boshladik",
    "quiz.progress": "Savol {index}/{total}",
    "quiz.scale_hint": "0️⃣ {low}   ·   5️⃣ {high}",
    "quiz.back": "⬅️ Orqaga",
    "quiz.result_header": "✨ <b>Tahlil tayyor!</b>",
    "quiz.result_type": "🧴 Teri turingiz: <b>{skin_type}</b>",
    "quiz.recs_header": "📋 <b>Sizga tavsiyalar</b>",
    "quiz.done_footer": (
        "Bu tavsiyalar profilingizda saqlandi. Savolingiz bo'lsa — "
        "«✍️ Savol / Murojaat» tugmasini bosing."
    ),
    "quiz.retake": "🔄 Testni qayta topshirish",
    "quiz.saved_points": "💎 Test uchun <b>{points}</b> ball qo'shildi!",
    # Question texts — the legend goes in the message, the buttons are digits.
    "quiz.q1": (
        "Yuzingizni yuvgandan keyin 1 soat davomida hech qanday krem surtilmasa, "
        "teringiz qanday holatda bo'ladi?"
    ),
    "quiz.q1.opt0": "0 · Juda quruq tortiladi",
    "quiz.q1.opt1": "1 · Biroz quruq",
    "quiz.q1.opt2": "2 · Yonoqlar quruq, T-zona yog'li",
    "quiz.q1.opt3": "3 · Balanslangan",
    "quiz.q1.opt4": "4 · Yog'lanadi",
    "quiz.q1.opt5": "5 · Juda tez yog'lanadi",
    "quiz.q2": "Yuzingizda poralar qanchalik katta ko'rinadi?",
    "quiz.q2.low": "umuman sezilarli emas",
    "quiz.q2.high": "judayam sezilarli",
    "quiz.q3": "Teringizda allergik reaksiyalar qanchalik tez-tez uchraydi?",
    "quiz.q3.low": "umuman uchramagan",
    "quiz.q3.high": "juda tez-tez",
    "quiz.q4": "Yuzingizda husnbuzarlar qanchalik tez-tez paydo bo'ladi?",
    "quiz.q4.low": "umuman chiqmaydi",
    "quiz.q4.high": "har doim chiqadi",
    "quiz.q5": "Yuzingizda qora nuqtalar qanchalik ko'p?",
    "quiz.q5.low": "umuman yo'q",
    "quiz.q5.high": "judayam ko'p",
    "quiz.q6": "Yuzingizda oq nuqtalar (jiroviklar) qanchalik ko'p?",
    "quiz.q6.low": "umuman yo'q",
    "quiz.q6.high": "judayam ko'p",
    "quiz.q7": "Teringiz dog'ga, pigmentatsiyaga moyilmi?",
    "quiz.q7.low": "umuman moyil emas",
    "quiz.q7.high": "judayam moyil",
    "quiz.q8": "Ko'z atrofida mayda ajinlar qanchalik ko'rinadi?",
    "quiz.q8.low": "umuman sezilmaydi",
    "quiz.q8.high": "judayam sezilarli",
    "quiz.q9": "Ko'z tagida qorayishlar bormi?",
    "quiz.q9.low": "umuman yo'q",
    "quiz.q9.high": "judayam to'q",
    "quiz.q10": (
        "Yuz terisi qanchalik bo'shashgan yoki tarangligini yo'qotgan "
        "(osilishlar sezilarlimi)?"
    ),
    "quiz.q10.low": "umuman yo'qotmagan",
    "quiz.q10.high": "judayam yo'qotgan, osilish ko'p",
    # Base recommendation per skin type
    "rec.base.dry": (
        "💧 <b>Quruq teri</b>\n"
        "• Yumshoq, ko'piksiz tozalovchi — sulfatsiz\n"
        "• Spirtsiz toner, keyin darrov namlantiruvchi\n"
        "• Kremni <i>nam</i> teriga suring — namlikni qulflaydi\n"
        "• Kechqurun boyroq (qalinroq) krem yoki moy\n"
        "• Ertalab SPF 30+ — albatta"
    ),
    "rec.base.oily": (
        "🫧 <b>Yog'li teri</b>\n"
        "• Kuniga 2 marta yengil gel/penka bilan tozalash — ko'p emas\n"
        "• Niasinamid yoki rux tarkibli serum\n"
        "• Yengil, komedogen bo'lmagan namlantiruvchi — yog'li teri ham "
        "namlikka muhtoj\n"
        "• Haftada 1–2 marta BHA (salitsil kislota)\n"
        "• SPF — yengil, gel formulada"
    ),
    "rec.base.normal": (
        "🌿 <b>Normal teri</b>\n"
        "• Muvozanatni saqlang: tozalash → toner → namlantirish\n"
        "• Haftada 1 marta yengil eksfoliatsiya kifoya\n"
        "• Antioksidant (C vitamini) ertalab\n"
        "• Mavsumga qarab kremni almashtiring\n"
        "• Ertalab SPF 30+"
    ),
    "rec.base.combined": (
        "⚖️ <b>Aralash teri</b>\n"
        "• T-zonaga (peshona, burun, iyak) yengil vosita, yonoqlarga boyroq krem\n"
        "• Haftada 1 marta yumshoq eksfoliatsiya\n"
        "• Toner butun yuzga, namlantiruvchi zonaga qarab\n"
        "• Og'ir, yog'li kremlardan saqlaning\n"
        "• Ertalab SPF unutmang"
    ),
    "rec.base.sensitive": (
        "🌸 <b>Sezgir teri</b>\n"
        "• Har yangi mahsulotni bilak terisida 24 soat sinang\n"
        "• Atirsiz (fragrance-free) formulalar\n"
        "• Skrablardan saqlaning — yumshoq kimyoviy eksfoliant ma'qul\n"
        "• Kam vosita — yaxshi: 3–4 bosqichli sodda parvarish\n"
        "• Mineral (fizik) SPF ko'proq mos keladi"
    ),
    # Problem-specific add-ons (triggered when the answer is 3 or more)
    "rec.P0": (
        "🕳 <b>Kengaygan poralar</b>\n"
        "Niasinamid (5%) va haftada 2 marta BHA poralarni toraytiradi. "
        "Kunlik SPF shart — quyosh poralarni kattalashtiradi."
    ),
    "rec.S": (
        "🌡 <b>Sezgirlik / allergiya</b>\n"
        "Tarkibni soddalashtiring: tozalovchi + namlantiruvchi + SPF. "
        "Sentella, panthenol, seramid izlang; kislota va retinoidni vaqtincha "
        "to'xtating."
    ),
    "rec.Bh": (
        "⚫️ <b>Qora nuqtalar</b>\n"
        "Salitsil kislota (BHA) haftada 2–3 marta. Qo'l bilan siqmang — "
        "dog' va yallig'lanish qoladi."
    ),
    "rec.Wh": (
        "⚪️ <b>Oq nuqtalar (jiroviklar)</b>\n"
        "Yengil AHA/BHA va adapalen yordam beradi. Og'ir yog'li kremlarni "
        "yengil gelga almashtiring."
    ),
    "rec.P": (
        "🟤 <b>Dog' va pigmentatsiya</b>\n"
        "Ertalab C vitamini, kechqurun niasinamid yoki alfa-arbutin. "
        "SPF 50 — pigmentatsiyaga qarshi eng kuchli vosita."
    ),
    "rec.Ew": (
        "👁 <b>Ko'z atrofi ajinlari</b>\n"
        "Peptid yoki past dozali retinolli ko'z kremi kechqurun. "
        "Nozik teriga barmoq uchi bilan ohista suring."
    ),
    "rec.Ed": (
        "🌙 <b>Ko'z tagi qorayishi</b>\n"
        "Kofein tarkibli ko'z serumi, sovuq kompress va uyqu rejimi. "
        "K vitamini va niasinamid qon aylanishiga yordam beradi."
    ),
    "rec.W": (
        "🪢 <b>Bo'shashish va tarangligini yo'qotish</b>\n"
        "Kechqurun retinoid, ertalab peptid + SPF. Massaj va yuz gimnastikasi "
        "qo'shimcha samara beradi."
    ),
    "rec.Ao": (
        "🔴 <b>Husnbuzar (yog'li teri)</b>\n"
        "BHA + benzoil peroksid yoki adapalen. Yengil, moysiz namlantiruvchi. "
        "Uzoq davom etsa — dermatologga murojaat qiling."
    ),
    "rec.Ad": (
        "🔴 <b>Husnbuzar (quruq/sezgir teri)</b>\n"
        "Kuchli quritadigan vositalardan saqlaning. Azelain kislota va "
        "niasinamid yumshoq ishlaydi, teri to'sig'ini buzmaydi."
    ),
    # ------------------------------------------------------------- products
    "purchase.thanks": (
        "🛍 Xaridingiz uchun rahmat!\n\n"
        "Quyida mahsulotdan qanday foydalanish bo'yicha qo'llanma. "
        "Bir haftadan so'ng natijangizni so'raymiz 😊"
    ),
    "product.none": "Sizda hozircha mahsulotlar yo'q.",
    "tutorial.intro_fallback": "📘 <b>{product}</b> uchun qo'llanma",
    "tutorial.video_soon": "⏳ Ushbu bosqich uchun video tez orada qo'shiladi.",
    "tutorial.step_not_found": "Bosqich topilmadi.",
    "catalog.header": "🛍 <b>Bizning mahsulotlar:</b>",
    "catalog.empty": "Katalog hozircha bo'sh. Tez orada to'ldiriladi!",
    "catalog.footer": (
        "📍 Xarid qilish uchun do'konimizga keling yoki "
        "«✍️ Savol / Murojaat» orqali yozing — yordam beramiz."
    ),
    "top.header": "🔥 <b>{month} oyining top mahsulotlari</b>",
    "top.empty": (
        "Hozircha bu oyning top ro'yxati to'ldirilmagan. Tez orada e'lon "
        "qilamiz — kuzatib boring!"
    ),
    "top.footer": (
        "🏷 Bu mahsulotlar shu oyda eng ko'p tanlangan. Savolingiz bo'lsa — "
        "«✍️ Savol / Murojaat» tugmasini bosing."
    ),
    "top.rank": "#{rank}",
    # ------------------------------------------------------------- feedback
    "feedback.ask_rating": "⭐️ Mahsulotni 1 dan 5 gacha baholang:",
    "feedback.ask_text": (
        "💬 Qo'shimcha fikr yozasizmi? (ixtiyoriy)\n\n"
        "Nima yoqdi, nima yoqmadi — yozib qoldiring, "
        "yoki pastdagi tugma bilan o'tkazib yuboring."
    ),
    "feedback.thanks_fallback": "🙏 Fikringiz uchun rahmat!",
    "feedback.save_error": "Fikrni saqlab bo'lmadi. Keyinroq urinib ko'ring.",
    "feedback.pick_product": "Qaysi mahsulotga baho bermoqchisiz?",
    # -------------------------------------------------------------- support
    "support.ask": (
        "✍️ Savolingiz yoki murojaatingizni yozing.\n\n"
        "Matn yoki rasm yuborishingiz mumkin — jamoamiz shu yerda javob beradi.\n"
        "Menyuga qaytish uchun pastdagi tugmalardan foydalaning."
    ),
    "support.empty": "Iltimos, matn yozing yoki rasm yuboring.",
    "support.saved": (
        "✅ Qabul qilindi! Jamoamiz tez orada shu yerda javob beradi.\n\n"
        "Yana yozmoqchi bo'lsangiz — shunchaki davom eting 👇"
    ),
    "support.save_error": "Murojaatni saqlab bo'lmadi. Keyinroq urinib ko'ring.",
    "support.reply_btn": "✍️ Javob yozish",
    "support.rate_limited": (
        "⏳ Juda ko'p xabar yubordingiz. Iltimos, bir oz kutib, keyin qayta "
        "urinib ko'ring."
    ),
    "support.no_unanswered": "✅ Javobsiz murojaatlar yo'q.",
    "support.unanswered_header": "🔁 Javobsiz murojaatlar qayta yuborilmoqda: {count}",
    # ------------------------------------------------------------- progress
    "progress.ask_before": "📷 Avval <b>OLDIN</b> rasmingizni yuboring.",
    "progress.ask_after": "📷 Endi <b>KEYIN</b> rasmingizni yuboring.",
    "progress.not_photo": "Iltimos, matn emas, rasm yuboring.",
    "progress.save_error": "Rasmni saqlab bo'lmadi. Qaytadan urinib ko'ring.",
    "progress.done": "🙏 Rahmat! Jamoamiz natijangizni ko'rib chiqadi.",
    # ------------------------------------------------------------ discounts
    "discount.none": "Hozircha faol chegirmalar yo'q.",
    "discount.header": "🎁 <b>Faol chegirmalar:</b>",
    "discount.until": "⏳ {date} gacha",
    # -------------------------------------------------------------- loyalty
    "loyalty.disabled": (
        "Bonus dasturi hozircha yopiq. Tez orada qaytadi — kuzatib boring!"
    ),
    "loyalty.header": "💎 <b>Bonus hisobingiz</b>",
    "loyalty.balance": "🪙 Ballaringiz: <b>{points}</b>",
    "loyalty.tier": "🏅 Darajangiz: <b>{tier}</b> — keshbek {cashback}%",
    "loyalty.next_tier": (
        "⬆️ <b>{next_tier}</b> darajasiga <b>{remaining}</b> ball qoldi\n{bar}"
    ),
    "loyalty.max_tier": "👑 Siz eng yuqori darajadasiz. Rahmat!",
    "loyalty.lifetime": "📈 Jami yig'ilgan: {lifetime} ball",
    "loyalty.how_to_earn": (
        "<b>Ball qanday yig'iladi</b>\n"
        "• Har xariddan — {purchase} ball\n"
        "• Mahsulotga baho — {feedback} ball\n"
        "• Oldin/keyin rasmi — {progress} ball\n"
        "• Do'stingizni taklif qilsangiz — {referral} ball\n"
        "• Tug'ilgan kuningizda — {birthday} ball"
    ),
    "loyalty.rewards_btn": "🎁 Ballni sarflash",
    "loyalty.history_btn": "🧾 Tarix",
    "loyalty.rewards_header": (
        "🎁 <b>Ballga almashtiriladigan sovg'alar</b>\n\nBalansingiz: <b>{points}</b> ball"
    ),
    "loyalty.rewards_empty": "Hozircha sovg'alar ro'yxati bo'sh. Tez orada qo'shamiz!",
    "loyalty.reward_line": "{title} — <b>{cost}</b> ball",
    "loyalty.redeem_ok": (
        "🎉 <b>{title}</b> sizniki!\n\n"
        "🔑 Promokod: <code>{code}</code>\n"
        "Do'konda shu kodni ko'rsating.\n\n"
        "Qolgan balansingiz: <b>{points}</b> ball"
    ),
    "loyalty.redeem_not_enough": (
        "😔 Ball yetarli emas. Kerak: <b>{cost}</b>, sizda: <b>{points}</b>.\n"
        "Xarid qiling yoki fikr qoldiring — ball yig'iladi."
    ),
    "loyalty.redeem_error": "Almashtirib bo'lmadi. Keyinroq urinib ko'ring.",
    "loyalty.redeem_unavailable": "Bu sovg'a hozir mavjud emas.",
    "loyalty.history_header": "🧾 <b>Oxirgi harakatlar</b>",
    "loyalty.history_empty": "Hozircha harakat yo'q. Birinchi xaridingizdan keyin paydo bo'ladi.",
    "loyalty.history_line": "{sign}{points} — {reason} · {date}",
    "loyalty.tier.bronze": "Bronza",
    "loyalty.tier.silver": "Kumush",
    "loyalty.tier.gold": "Oltin",
    "loyalty.tier.platinum": "Platina",
    "loyalty.reason.purchase": "Xarid",
    "loyalty.reason.feedback": "Mahsulotga baho",
    "loyalty.reason.progress": "Natija rasmi",
    "loyalty.reason.referral": "Do'st taklifi",
    "loyalty.reason.birthday": "Tug'ilgan kun sovg'asi",
    "loyalty.reason.quiz": "Teri testi",
    "loyalty.reason.registration": "Ro'yxatdan o'tish",
    "loyalty.reason.redeem": "Sovg'aga almashtirildi",
    "loyalty.reason.manual": "Admin tuzatishi",
    "loyalty.earned": "💎 <b>+{points}</b> ball qo'shildi — {reason}. Jami: <b>{total}</b>",
    "loyalty.tier_up": (
        "🎊 Tabriklaymiz! Siz <b>{tier}</b> darajasiga ko'tarildingiz.\n"
        "Endi keshbegingiz — <b>{cashback}%</b>."
    ),
    # -------------------------------------------------------------- profile
    "profile.template": (
        "👤 <b>Profilingiz</b>\n\n"
        "Ism: {full_name}\n"
        "Telefon: {phone}\n"
        "Tug'ilgan sana: {birth_date}\n"
        "Teri turi: {face}\n"
        "Mahsulotlar: {products}\n"
        "Bonus: {points} ball · {tier}"
    ),
    # ------------------------------------------------------------- fallback
    "fallback.unknown": (
        "Sizni tushunmadim 🤔\n\n"
        "Pastdagi menyudan kerakli bo'limni tanlang. Savolingiz bo'lsa — "
        "«✍️ Savol / Murojaat» tugmasini bosing."
    ),
    "fallback.stale_button": "Bu tugma eskirgan. /menu ni bosing.",
    # ----------------------------------------------------------------- help
    "help.text": (
        "ℹ️ <b>Real Beauty bot</b>\n\n"
        "• 🧪 Qaysi tarkiblarni o'rganamiz — siz olgan mahsulotlar tarkibi va "
        "video darslar\n"
        "• 🛍 Mahsulotlar — do'konimizdagi barcha mahsulotlar katalogi\n"
        "• 🔥 Bu oydagi top mahsulotlar — shu oyning eng zo'r tanlovlari\n"
        "• ⭐️ Mahsulotga baho — olgan mahsulotingizga yulduz va fikr "
        "qoldirasiz\n"
        "• ✍️ Savol / Murojaat — jamoamiz bilan jonli yozishma\n"
        "• 🎁 Chegirmalar — joriy aksiyalar va promokodlar\n"
        "• 💎 Bonuslarim — ballaringiz, darajangiz va sovg'alar\n"
        "• 👤 Profil — ma'lumotlaringiz va til sozlamasi\n\n"
        "Menyuni ochish uchun /menu buyrug'ini yuboring."
    ),
    # --------------------------------------------------------------- seller
    "seller.only": "⛔️ Bu buyruq faqat sotuvchilar uchun.",
    "seller.link": "🔗 Sizning referal havolangiz:\n<code>{link}</code>",
    "admin.user_started": (
        "🆕 Yangi foydalanuvchi referal havolangiz orqali start bosdi.\n"
        "Telegram ID: <code>{telegram_id}</code>\n"
        "Holat: to'ldirilishi kutilmoqda."
    ),
    "admin.user_registered": "✅ <b>{full_name}</b> muvaffaqiyatli ro'yxatdan o'tdi.",
    # ------------------------------------------------------- bot command menu
    "cmd.start": "Botni ishga tushirish",
    "cmd.menu": "Asosiy menyu",
    "cmd.help": "Yordam",
    "cmd.language": "Tilni o'zgartirish",
}
