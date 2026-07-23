"""English strings — mirrors every key in `uz.py`."""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # ------------------------------------------------------------------ menu
    "menu.ingredients": "🧪 Ingredients we study",
    "menu.catalog": "🛍 Products",
    "menu.top": "🔥 Top products this month",
    "menu.feedback": "⭐️ Rate a product",
    "menu.support": "✍️ Question / Request",
    "menu.discounts": "🎁 Discounts",
    "menu.bonus": "💎 My bonuses",
    "menu.profile": "👤 Profile",
    "menu.help": "ℹ️ Help",
    "menu.legacy_tutorials": "📚 Tutorials",
    "menu.legacy_feedback": "💬 Leave feedback",
    "menu.legacy_tips": "💡 Tips",
    "menu.opened": "Main menu. Pick a section 👇",
    # -------------------------------------------------------------- language
    "lang.choose": (
        "🌐 <b>Tilni tanlang / Выберите язык / Choose a language</b>\n\n"
        "Every message and button in the bot will use the language you pick."
    ),
    "lang.changed": "✅ Language changed. Use the menu 👇",
    "lang.button": "🌐 Change language",
    # ---------------------------------------------------------- registration
    "reg.greeting_self": (
        "👋 Welcome to <b>Real Beauty</b>!\n\n"
        "To register, please type your full name."
    ),
    "reg.greeting_admin": (
        "👋 <b>{admin_name}</b> will help you register.\n\n"
        "Please type your full name."
    ),
    "reg.ask_name": "Please type your full name.",
    "reg.name_short": "That name is too short. Please type your full name.",
    "reg.name_invalid": "Names should contain letters only. Please try again.",
    "reg.ask_birth": "📅 What is your date of birth? (dd.mm.yyyy)",
    "reg.invalid_date": (
        "❌ That date isn't valid. Use <b>dd.mm.yyyy</b> "
        "(for example: 25.12.1995)."
    ),
    "reg.date_future": "❌ A birth date can't be in the future. Please try again.",
    "reg.date_old": "❌ That date looks too far back. Please check and try again.",
    "reg.ask_phone": "📱 What is your phone number?",
    "reg.ask_phone_again": "Please send or type your phone number.",
    "reg.invalid_phone": (
        "❌ That number isn't valid. For example: <b>+998 90 123 45 67</b>\n"
        "Or share your contact with the button below."
    ),
    "reg.contact_not_yours": (
        "❌ That's somebody else's contact. Please send your own number."
    ),
    "reg.share_contact": "📱 Share contact",
    "reg.ask_photo": "📷 Send a photo of yourself (optional).",
    "reg.skip": "⏭ Skip",
    "reg.saved_fallback": "✅ Registration complete! Welcome to Real Beauty.",
    "reg.error": "Something went wrong while saving. Please press /start again.",
    "reg.invalid_ref": "That referral link is invalid. You can register on your own.",
    # -------------------------------------------------------------- account
    "user.welcome_back": (
        "👋 Great to see you again, <b>{name}</b>!\n\n"
        "Your details are saved. Use the menu 👇"
    ),
    "user.disabled": (
        "⛔️ Your account is temporarily inactive.\n\n"
        "If you have questions, please contact our shop."
    ),
    "user.not_registered": "Please press /start and register first.",
    # ----------------------------------------------------------- skin / quiz
    "skin.know_question": (
        "🧴 <b>Do you know your skin type?</b>\n\n"
        "If you do, we'll set it right away. If not, we'll find it together "
        "with 10 short questions — about a minute."
    ),
    "skin.know_yes": "✅ Yes, I know it",
    "skin.know_no": "🔍 No, help me find out",
    "skin.pick": "Pick your skin type 👇",
    "skin.type.dry": "Dry",
    "skin.type.oily": "Oily",
    "skin.type.combined": "Combination",
    "skin.type.normal": "Normal",
    "skin.type.sensitive": "Sensitive",
    "quiz.intro": (
        "🔍 <b>Let's find your skin type</b>\n\n"
        "We'll ask 10 simple questions. Rate each one <b>from 0 to 5</b> — "
        "0 means \"not at all\", 5 means \"very much\".\n\n"
        "At the end you get your skin type and a care plan made for you. Ready?"
    ),
    "quiz.start": "🚀 Let's go",
    "quiz.progress": "Question {index}/{total}",
    "quiz.scale_hint": "0️⃣ {low}   ·   5️⃣ {high}",
    "quiz.back": "⬅️ Back",
    "quiz.result_header": "✨ <b>Your analysis is ready!</b>",
    "quiz.result_type": "🧴 Your skin type: <b>{skin_type}</b>",
    "quiz.recs_header": "📋 <b>Recommendations for you</b>",
    "quiz.done_footer": (
        "These recommendations are saved in your profile. Any questions — tap "
        "«✍️ Question / Request»."
    ),
    "quiz.retake": "🔄 Retake the quiz",
    "quiz.saved_points": "💎 <b>{points}</b> points added for the quiz!",
    "quiz.q1": (
        "One hour after washing your face, with no cream applied, how does "
        "your skin feel?"
    ),
    "quiz.q1.opt0": "0 · Very tight and dry",
    "quiz.q1.opt1": "1 · Slightly dry",
    "quiz.q1.opt2": "2 · Dry cheeks, oily T-zone",
    "quiz.q1.opt3": "3 · Balanced",
    "quiz.q1.opt4": "4 · Gets oily",
    "quiz.q1.opt5": "5 · Gets oily very fast",
    "quiz.q2": "How visible are the pores on your face?",
    "quiz.q2.low": "not visible at all",
    "quiz.q2.high": "very visible",
    "quiz.q3": "How often do you get allergic reactions on your skin?",
    "quiz.q3.low": "never had one",
    "quiz.q3.high": "very often",
    "quiz.q4": "How often do breakouts (pimples) appear?",
    "quiz.q4.low": "never",
    "quiz.q4.high": "all the time",
    "quiz.q5": "How many blackheads do you have?",
    "quiz.q5.low": "none at all",
    "quiz.q5.high": "a great many",
    "quiz.q6": "How many whiteheads (milia) do you have?",
    "quiz.q6.low": "none at all",
    "quiz.q6.high": "a great many",
    "quiz.q7": "Is your skin prone to dark spots and pigmentation?",
    "quiz.q7.low": "not at all",
    "quiz.q7.high": "very prone",
    "quiz.q8": "How visible are fine lines around your eyes?",
    "quiz.q8.low": "not visible at all",
    "quiz.q8.high": "very visible",
    "quiz.q9": "Do you have dark circles under your eyes?",
    "quiz.q9.low": "none at all",
    "quiz.q9.high": "very dark",
    "quiz.q10": (
        "How much firmness has your facial skin lost (is sagging noticeable)?"
    ),
    "quiz.q10.low": "none at all",
    "quiz.q10.high": "a lot, plenty of sagging",
    "rec.base.dry": (
        "💧 <b>Dry skin</b>\n"
        "• Gentle, non-foaming cleanser — sulfate free\n"
        "• Alcohol-free toner, moisturiser straight after\n"
        "• Apply cream to <i>damp</i> skin — it locks the water in\n"
        "• A richer cream or facial oil at night\n"
        "• SPF 30+ every morning — no exceptions"
    ),
    "rec.base.oily": (
        "🫧 <b>Oily skin</b>\n"
        "• Cleanse twice a day with a light gel/foam — no more than that\n"
        "• A niacinamide or zinc serum\n"
        "• Light, non-comedogenic moisturiser — oily skin needs water too\n"
        "• BHA (salicylic acid) once or twice a week\n"
        "• SPF — light, gel formula"
    ),
    "rec.base.normal": (
        "🌿 <b>Normal skin</b>\n"
        "• Keep the balance: cleanse → tone → moisturise\n"
        "• One gentle exfoliation a week is plenty\n"
        "• An antioxidant (vitamin C) in the morning\n"
        "• Switch cream with the season\n"
        "• SPF 30+ every morning"
    ),
    "rec.base.combined": (
        "⚖️ <b>Combination skin</b>\n"
        "• Light products on the T-zone (forehead, nose, chin), richer cream "
        "on the cheeks\n"
        "• Gentle exfoliation once a week\n"
        "• Toner over the whole face, moisturiser by zone\n"
        "• Avoid heavy, greasy creams\n"
        "• Don't skip SPF in the morning"
    ),
    "rec.base.sensitive": (
        "🌸 <b>Sensitive skin</b>\n"
        "• Patch-test every new product on your wrist for 24 hours\n"
        "• Choose fragrance-free formulas\n"
        "• Skip scrubs — a mild chemical exfoliant is kinder\n"
        "• Fewer products is better: a simple 3–4 step routine\n"
        "• Mineral (physical) SPF suits you best"
    ),
    "rec.P0": (
        "🕳 <b>Enlarged pores</b>\n"
        "Niacinamide (5%) plus BHA twice a week tightens pores. Daily SPF is "
        "essential — sun damage makes pores look larger."
    ),
    "rec.S": (
        "🌡 <b>Sensitivity / allergies</b>\n"
        "Simplify your routine: cleanser + moisturiser + SPF. Look for "
        "centella, panthenol and ceramides; pause acids and retinoids for now."
    ),
    "rec.Bh": (
        "⚫️ <b>Blackheads</b>\n"
        "Salicylic acid (BHA) two or three times a week. Don't squeeze them — "
        "that leaves marks and inflammation."
    ),
    "rec.Wh": (
        "⚪️ <b>Whiteheads (milia)</b>\n"
        "Mild AHA/BHA and adapalene help. Swap heavy, greasy creams for a "
        "light gel."
    ),
    "rec.P": (
        "🟤 <b>Spots and pigmentation</b>\n"
        "Vitamin C in the morning, niacinamide or alpha-arbutin at night. "
        "SPF 50 is the strongest anti-pigmentation tool there is."
    ),
    "rec.Ew": (
        "👁 <b>Fine lines around the eyes</b>\n"
        "An eye cream with peptides or low-dose retinol at night. Pat it into "
        "that thin skin gently with a fingertip."
    ),
    "rec.Ed": (
        "🌙 <b>Dark circles</b>\n"
        "A caffeine eye serum, a cold compress and a steady sleep schedule. "
        "Vitamin K and niacinamide support circulation."
    ),
    "rec.W": (
        "🪢 <b>Loss of firmness</b>\n"
        "Retinoid at night, peptides + SPF in the morning. Facial massage and "
        "exercises add to the effect."
    ),
    "rec.Ao": (
        "🔴 <b>Breakouts (oily skin)</b>\n"
        "BHA plus benzoyl peroxide or adapalene. A light, oil-free "
        "moisturiser. If it persists, see a dermatologist."
    ),
    "rec.Ad": (
        "🔴 <b>Breakouts (dry / sensitive skin)</b>\n"
        "Avoid harsh drying products. Azelaic acid and niacinamide work "
        "gently and keep your skin barrier intact."
    ),
    # ------------------------------------------------------------- products
    "purchase.thanks": (
        "🛍 Thank you for your purchase!\n\n"
        "Below is the guide on how to use it. We'll ask about your result in "
        "a week 😊"
    ),
    "product.none": "You don't have any products yet.",
    "tutorial.intro_fallback": "📘 Guide for <b>{product}</b>",
    "tutorial.video_soon": "⏳ The video for this step is coming soon.",
    "tutorial.step_not_found": "Step not found.",
    "catalog.header": "🛍 <b>Our products:</b>",
    "catalog.empty": "The catalogue is empty for now. We'll fill it soon!",
    "catalog.footer": (
        "📍 Visit our shop or write through «✍️ Question / Request» — "
        "we'll help you buy."
    ),
    "top.header": "🔥 <b>Top products of {month}</b>",
    "top.empty": (
        "This month's top list isn't filled in yet. We'll announce it soon — "
        "stay tuned!"
    ),
    "top.footer": (
        "🏷 These were the most-chosen products this month. Any questions — "
        "tap «✍️ Question / Request»."
    ),
    "top.rank": "#{rank}",
    # ------------------------------------------------------------- feedback
    "feedback.ask_rating": "⭐️ Rate the product from 1 to 5:",
    "feedback.ask_text": (
        "💬 Care to add a few words? (optional)\n\n"
        "What you liked, what you didn't — leave a note, or skip with the "
        "button below."
    ),
    "feedback.thanks_fallback": "🙏 Thank you for your feedback!",
    "feedback.save_error": "Couldn't save your feedback. Please try again later.",
    "feedback.pick_product": "Which product would you like to rate?",
    # -------------------------------------------------------------- support
    "support.ask": (
        "✍️ Write your question or request.\n\n"
        "You can send text or a photo — our team answers right here.\n"
        "Use the buttons below to go back to the menu."
    ),
    "support.empty": "Please write some text or send a photo.",
    "support.saved": (
        "✅ Got it! Our team will answer here shortly.\n\n"
        "Want to add more — just keep writing 👇"
    ),
    "support.save_error": "Couldn't save your request. Please try again later.",
    "support.reply_btn": "✍️ Write a reply",
    "support.rate_limited": (
        "⏳ That's a lot of messages at once. Please wait a moment and try again."
    ),
    "support.no_unanswered": "✅ No unanswered requests.",
    "support.unanswered_header": "🔁 Re-sending unanswered requests: {count}",
    # ------------------------------------------------------------- progress
    "progress.ask_before": "📷 First send your <b>BEFORE</b> photo.",
    "progress.ask_after": "📷 Now send your <b>AFTER</b> photo.",
    "progress.not_photo": "Please send a photo, not text.",
    "progress.save_error": "Couldn't save the photo. Please try again.",
    "progress.done": "🙏 Thank you! Our team will review your result.",
    # ------------------------------------------------------------ discounts
    "discount.none": "No active discounts right now.",
    "discount.header": "🎁 <b>Active discounts:</b>",
    "discount.until": "⏳ until {date}",
    # -------------------------------------------------------------- loyalty
    "loyalty.disabled": (
        "The bonus programme is closed for now. It will be back soon — stay tuned!"
    ),
    "loyalty.header": "💎 <b>Your bonus account</b>",
    "loyalty.balance": "🪙 Your points: <b>{points}</b>",
    "loyalty.tier": "🏅 Your tier: <b>{tier}</b> — {cashback}% cashback",
    "loyalty.next_tier": (
        "⬆️ <b>{remaining}</b> points to go until <b>{next_tier}</b>\n{bar}"
    ),
    "loyalty.max_tier": "👑 You're on the highest tier. Thank you!",
    "loyalty.lifetime": "📈 Earned in total: {lifetime} points",
    "loyalty.how_to_earn": (
        "<b>How points add up</b>\n"
        "• Every purchase — {purchase} points\n"
        "• Rating a product — {feedback} points\n"
        "• Before/after photos — {progress} points\n"
        "• Inviting a friend — {referral} points\n"
        "• On your birthday — {birthday} points"
    ),
    "loyalty.rewards_btn": "🎁 Spend points",
    "loyalty.history_btn": "🧾 History",
    "loyalty.rewards_header": (
        "🎁 <b>Rewards you can claim</b>\n\nYour balance: <b>{points}</b> points"
    ),
    "loyalty.rewards_empty": "No rewards listed yet. We'll add some soon!",
    "loyalty.reward_line": "{title} — <b>{cost}</b> points",
    "loyalty.redeem_ok": (
        "🎉 <b>{title}</b> is yours!\n\n"
        "🔑 Promo code: <code>{code}</code>\n"
        "Show it at the shop.\n\n"
        "Points left: <b>{points}</b>"
    ),
    "loyalty.redeem_not_enough": (
        "😔 Not enough points. Needed: <b>{cost}</b>, you have: <b>{points}</b>.\n"
        "Buy something or leave a review — points add up."
    ),
    "loyalty.redeem_error": "Couldn't redeem that. Please try again later.",
    "loyalty.redeem_unavailable": "That reward isn't available right now.",
    "loyalty.history_header": "🧾 <b>Recent activity</b>",
    "loyalty.history_empty": "Nothing here yet. It starts with your first purchase.",
    "loyalty.history_line": "{sign}{points} — {reason} · {date}",
    "loyalty.tier.bronze": "Bronze",
    "loyalty.tier.silver": "Silver",
    "loyalty.tier.gold": "Gold",
    "loyalty.tier.platinum": "Platinum",
    "loyalty.reason.purchase": "Purchase",
    "loyalty.reason.feedback": "Product rating",
    "loyalty.reason.progress": "Result photo",
    "loyalty.reason.referral": "Friend referral",
    "loyalty.reason.birthday": "Birthday gift",
    "loyalty.reason.quiz": "Skin quiz",
    "loyalty.reason.registration": "Registration",
    "loyalty.reason.redeem": "Redeemed for a reward",
    "loyalty.reason.manual": "Admin adjustment",
    "loyalty.earned": "💎 <b>+{points}</b> points — {reason}. Total: <b>{total}</b>",
    "loyalty.tier_up": (
        "🎊 Congratulations! You've reached the <b>{tier}</b> tier.\n"
        "Your cashback is now <b>{cashback}%</b>."
    ),
    # -------------------------------------------------------------- profile
    "profile.template": (
        "👤 <b>Your profile</b>\n\n"
        "Name: {full_name}\n"
        "Phone: {phone}\n"
        "Date of birth: {birth_date}\n"
        "Skin type: {face}\n"
        "Products: {products}\n"
        "Bonuses: {points} points · {tier}"
    ),
    # ------------------------------------------------------------- fallback
    "fallback.unknown": (
        "I didn't catch that 🤔\n\n"
        "Pick a section from the menu below. If you have a question, tap "
        "«✍️ Question / Request»."
    ),
    "fallback.stale_button": "That button is out of date. Press /menu.",
    # ----------------------------------------------------------------- help
    "help.text": (
        "ℹ️ <b>Real Beauty bot</b>\n\n"
        "• 🧪 Ingredients we study — what's in your products, plus video "
        "lessons\n"
        "• 🛍 Products — the full shop catalogue\n"
        "• 🔥 Top products this month — this month's best picks\n"
        "• ⭐️ Rate a product — leave stars and a review\n"
        "• ✍️ Question / Request — live chat with our team\n"
        "• 🎁 Discounts — current promotions and promo codes\n"
        "• 💎 My bonuses — your points, tier and rewards\n"
        "• 👤 Profile — your details and language setting\n\n"
        "Send /menu to open the menu."
    ),
    # --------------------------------------------------------------- seller
    "seller.only": "⛔️ This command is for sellers only.",
    "seller.link": "🔗 Your referral link:\n<code>{link}</code>",
    "admin.user_started": (
        "🆕 A new user pressed start through your referral link.\n"
        "Telegram ID: <code>{telegram_id}</code>\n"
        "Status: waiting to be filled in."
    ),
    "admin.user_registered": "✅ <b>{full_name}</b> completed registration.",
    # ------------------------------------------------------- bot command menu
    "cmd.start": "Start the bot",
    "cmd.menu": "Main menu",
    "cmd.help": "Help",
    "cmd.language": "Change language",
}
