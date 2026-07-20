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
        """
        import logging

        from jinja2 import Environment

        try:
            env = Environment(autoescape=False)
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
