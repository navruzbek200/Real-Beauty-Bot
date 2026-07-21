from __future__ import annotations

from typing import Any

from django.db import models


class MessageTemplate(models.Model):
    """
    Editable message template with Jinja2-style placeholders.
    Available context: {{ user.full_name }}, {{ product.name }},
                       {{ discount }}, {{ week }}, etc.
    """

    class TemplateType(models.TextChoices):
        WELCOME = "welcome", "Ro'yxatdan o'tgach salomlashish"
        PRODUCT_INTRO = "product_intro", "Mahsulot qo'llanmasi kirish"
        WEEK1_CHECKIN = "week1_checkin", "1-hafta so'rovi"
        WEEK2_PROGRESS = "week2_progress", "2-hafta natija so'rovi"
        BIRTHDAY_SALE = "birthday_sale", "Tug'ilgan kun chegirmasi"
        FEEDBACK_THANKS = "feedback_thanks", "Fikr uchun rahmat"

    name = models.CharField(max_length=128, unique=True, verbose_name="Nomi")
    # Unique: the senders pick a template by type, so a second row of the same
    # type would make which text goes out a coin flip.
    template_type = models.CharField(
        max_length=32,
        choices=TemplateType.choices,
        unique=True,
        verbose_name="Shablon turi",
    )
    body = models.TextField(
        verbose_name="Xabar matni",
        help_text="{{ o'zgaruvchi }} qo'llab-quvvatlanadi. "
        "Masalan: {{ user.full_name }}, {{ product.name }}, {{ discount }}. "
        "Telegram HTML formatidan foydalaning.",
    )
    parse_mode = models.CharField(
        max_length=8,
        default="HTML",
        choices=[("HTML", "HTML"), ("Markdown", "Markdown")],
        verbose_name="Format",
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")

    class Meta:
        verbose_name = "Xabar shabloni"
        verbose_name_plural = "Xabar shablonlari"

    def render(self, context: dict[str, Any]) -> str:
        """
        Render template body with given context dict.

        Falls back to the raw body on any Jinja error: templates are edited by
        hand in the admin, and one unclosed brace must degrade to a slightly
        odd message — not crash the campaign task into a retry loop that
        leaves every customer without their message.

        For HTML templates the substituted values are escaped (autoescape):
        a customer named "<3" would otherwise produce invalid HTML and make
        Telegram reject every campaign message addressed to them.
        """
        import logging

        from jinja2 import Environment

        try:
            env = Environment(autoescape=self.parse_mode == "HTML")
            template = env.from_string(self.body)
            return template.render(**context)
        except Exception:  # noqa: BLE001 — syntax or undefined-variable errors
            logging.getLogger(__name__).exception(
                "Template %s failed to render; sending raw body", self.pk
            )
            return self.body

    def __str__(self) -> str:
        return f"[{self.template_type}] {self.name}"


class CampaignLog(models.Model):
    """Records every message sent to a user."""

    user = models.ForeignKey(
        "users.TelegramUser", on_delete=models.CASCADE, verbose_name="Foydalanuvchi"
    )
    template = models.ForeignKey(
        MessageTemplate, on_delete=models.SET_NULL, null=True, verbose_name="Shablon"
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")
    success = models.BooleanField(default=True, verbose_name="Muvaffaqiyatli")
    error_detail = models.TextField(blank=True, verbose_name="Xato tafsiloti")

    class Meta:
        verbose_name = "Yuborilgan xabar"
        verbose_name_plural = "Yuborilgan xabarlar"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["-sent_at"]),
            models.Index(fields=["user", "-sent_at"]),
        ]

    def __str__(self) -> str:
        status = "OK" if self.success else "FAIL"
        return f"{self.user} — {self.template} [{status}]"


class Broadcast(models.Model):
    """
    A one-off announcement the shop pushes to customers on demand: a seminar,
    a new arrival, a flash sale — anything that is not one of the fixed
    lifecycle templates.

    Kept separate from MessageTemplate because the lifecycle templates are a
    closed set the bot fires automatically, while these are composed and sent
    by a person whenever news comes up.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        SENDING = "sending", "Yuborilmoqda"
        SENT = "sent", "Yuborildi"
        FAILED = "failed", "Xato"

    class Audience(models.TextChoices):
        ALL = "all", "Hamma (botga ulangan barcha xaridorlar)"
        BY_SKIN = "by_skin", "Teri turi bo'yicha"
        BY_PRODUCT = "by_product", "Mahsulot sotib olganlar"

    title = models.CharField(
        max_length=128,
        verbose_name="Sarlavha (faqat siz uchun)",
        help_text="Ro'yxatda ko'rinadi. Mijozga yuborilmaydi.",
    )
    body = models.TextField(
        verbose_name="Xabar matni",
        help_text="Mijozga boradigan matn. Telegram HTML: <b>qalin</b>, "
        "<i>qiya</i>, <a href='...'>havola</a>.",
    )
    photo = models.ImageField(
        upload_to="broadcasts/",
        blank=True,
        null=True,
        verbose_name="Rasm (ixtiyoriy)",
        help_text="Yuklasangiz, xabar rasm bilan boradi.",
    )
    audience = models.CharField(
        max_length=16,
        choices=Audience.choices,
        default=Audience.ALL,
        verbose_name="Kimlarga",
    )
    skin_condition = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teri turi",
        help_text="«Teri turi bo'yicha» tanlansagina ishlaydi.",
    )
    product = models.ForeignKey(
        "products.Product",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Mahsulot",
        help_text="«Mahsulot sotib olganlar» tanlansagina ishlaydi.",
    )

    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.DRAFT,
        editable=False,
        verbose_name="Holat",
    )
    total = models.PositiveIntegerField(default=0, editable=False, verbose_name="Jami")
    sent_count = models.PositiveIntegerField(
        default=0, editable=False, verbose_name="Yuborildi"
    )
    failed_count = models.PositiveIntegerField(
        default=0, editable=False, verbose_name="Yetmadi"
    )

    created_by = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")
    started_at = models.DateTimeField(null=True, blank=True, editable=False)
    finished_at = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def recipients(self):
        """
        Active, bot-linked customers this broadcast targets.

        Only linked users (telegram_id set) can be reached, and inactive ones
        were switched off on purpose — both are excluded regardless of filter.
        """
        from apps.users.models import TelegramUser

        qs = TelegramUser.objects.filter(is_active=True, telegram_id__isnull=False)
        if self.audience == self.Audience.BY_SKIN and self.skin_condition:
            qs = qs.filter(face_condition=self.skin_condition)
        elif self.audience == self.Audience.BY_PRODUCT and self.product_id:
            qs = qs.filter(userproduct__product_id=self.product_id)
        return qs.distinct()
