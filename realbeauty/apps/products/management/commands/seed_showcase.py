"""
Fill the catalogue with a realistic, ready-to-demo skincare line: products with
descriptions and prices, some marked "top of the month" with a discount, and
multi-step video lessons attached (a couple of steps deliberately have no intro
text, to show that field is optional). Idempotent — safe to re-run, and safe on
production: it only touches products and their lessons, never customers.

    python manage.py seed_showcase
"""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from apps.products.models import Product, ProductTutorialStep

# name, description, price, old_price, top_order(0=not top), top_note, steps
# steps: list of (button_label, intro_text)  — intro_text "" means "optional, left blank"
CATALOGUE: list[dict[str, Any]] = [
    {
        "name": "Vitamin C Serum ✨",
        "description": (
            "Teriga yorqinlik beruvchi C vitaminli serum. Dog'larni "
            "oqartiradi, teri rangini tenglashtiradi. Ertalab, SPF'dan oldin."
        ),
        "price": 149000,
        "old_price": 199000,
        "top": 1,
        "top_note": "🔥 Eng ko'p sotilgan",
        "steps": [
            ("1-qadam: Tozalash", "Yuzni yumshoq ko'pik bilan yuving va quriting."),
            ("2-qadam: Serum surtish", "3-4 tomchi serumni yuzga teng yoying."),
            ("3-qadam: Namlash", ""),
        ],
    },
    {
        "name": "Tungi tiklovchi krem 🌙",
        "description": (
            "Uyqu paytida terini tiklaydi va namlaydi. Retinol va seramid "
            "bilan. Kechqurun, tozalangan teriga."
        ),
        "price": 189000,
        "old_price": None,
        "top": 2,
        "top_note": "🌙 Tunggi parvarish",
        "steps": [
            ("1-qadam: Tayyorlash", "Toner bilan terini tayyorlang."),
            ("2-qadam: Krem", ""),
        ],
    },
    {
        "name": "SPF 50 Quyoshdan himoya ☀️",
        "description": (
            "Har kunlik yengil quyoshdan himoya. Oq iz qoldirmaydi, "
            "makiyaj ostiga mos. UVA/UVB himoya."
        ),
        "price": 129000,
        "old_price": 159000,
        "top": 3,
        "top_note": "☀️ Har kuni shart",
        "steps": [
            ("Qanday surtiladi", "Parvarishning eng oxirida, chiqishdan 15 daqiqa oldin."),
        ],
    },
    {
        "name": "Hyaluron namlovchi toner 💧",
        "description": (
            "Gialuron kislotali toner terini chuqur namlaydi va keyingi "
            "vositalarni yaxshiroq singdiradi."
        ),
        "price": 89000,
        "old_price": None,
        "top": 0,
        "top_note": "",
        "steps": [
            ("Ishlatish tartibi", "Tozalashdan keyin paxta yoki kaft bilan surting."),
        ],
    },
    {
        "name": "Niasinamid tekislovchi serum 🧴",
        "description": (
            "Yog' balansini tartibga soladi, teshiklarni toraytiradi. "
            "Yog'li va aralash teri uchun ideal."
        ),
        "price": 119000,
        "old_price": 139000,
        "top": 0,
        "top_note": "",
        "steps": [],  # a product with no lessons yet — bot says "coming soon"
    },
    {
        "name": "Yumshoq tozalovchi ko'pik 🫧",
        "description": (
            "Kunlik yumshoq ko'pik terini quritmasdan tozalaydi. "
            "Barcha teri turlari uchun."
        ),
        "price": 69000,
        "old_price": None,
        "top": 0,
        "top_note": "",
        "steps": [
            ("1-qadam: Ho'llash", "Yuzni iliq suv bilan ho'llang."),
            ("2-qadam: Ko'piklash", "Bir oz ko'pikni kaftda ko'piklab yuzga surting."),
            ("3-qadam: Yuvish", ""),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed a realistic demo catalogue (products + lessons + top picks)."

    def handle(self, *args: Any, **opts: Any) -> None:
        for item in CATALOGUE:
            product, _ = Product.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "current_price": item["price"],
                    "old_price": item["old_price"],
                    "is_active": True,
                    "is_top": bool(item["top"]),
                    "top_order": item["top"] or 1,
                    "top_note": item["top_note"],
                },
            )
            # Rebuild this product's lessons so re-runs stay clean.
            product.tutorial_steps.all().delete()
            for order, (label, intro) in enumerate(item["steps"], start=1):
                ProductTutorialStep.objects.create(
                    product=product,
                    order=order,
                    button_label=label,
                    intro_text=intro,
                )
            steps = len(item["steps"])
            top = "TOP" if item["top"] else "—"
            self.stdout.write(f"• {item['name']} [{top}] · {steps} dars")

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ {len(CATALOGUE)} ta namuna mahsulot tayyor "
                "(darslar + top + chegirmalar bilan)."
            )
        )
