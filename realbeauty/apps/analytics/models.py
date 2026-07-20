from __future__ import annotations

from django.db import models


class UserFeedback(models.Model):
    user = models.ForeignKey(
        "users.TelegramUser", on_delete=models.CASCADE, verbose_name="Foydalanuvchi"
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Mahsulot",
    )
    week = models.PositiveSmallIntegerField(verbose_name="Hafta")  # 1 or 2
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Baho (1-5)"
    )
    text = models.TextField(blank=True, verbose_name="Fikr matni")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")

    # Admin reply → sent back to the customer in the bot.
    admin_reply = models.TextField(
        blank=True,
        verbose_name="Javob (mijozga yuboriladi)",
        help_text="Bu yerga yozib saqlasangiz, matn botda mijozga yuboriladi.",
    )
    reply_sent = models.BooleanField(
        default=False, editable=False, verbose_name="Javob yuborildi"
    )

    class Meta:
        verbose_name = "Fikr"
        verbose_name_plural = "Fikrlar"
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"{self.user} — {self.week}-hafta — {self.rating}"


class ProgressPhoto(models.Model):
    """
    A before/after photo.

    Storage is deliberately split: the full-size original stays on Telegram's
    servers and is addressed by `file_id` (free, permanent, fetched on demand),
    while our disk only ever holds a small thumbnail for the admin gallery.
    At ~40 KB each, 10k photos cost ~400 MB instead of ~20 GB.
    """

    THUMBNAIL_SIZE = (400, 400)

    class Label(models.TextChoices):
        BEFORE = "before", "Oldin"
        AFTER = "after", "Keyin"

    user = models.ForeignKey(
        "users.TelegramUser", on_delete=models.CASCADE, verbose_name="Foydalanuvchi"
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Mahsulot",
    )
    # Original on Telegram — the source of truth, never deleted.
    file_id = models.CharField(
        max_length=512, blank=True, editable=False, verbose_name="Telegram file_id"
    )
    thumbnail = models.ImageField(
        upload_to="progress_thumbs/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Kichik nusxa",
    )
    thumbnail_purged = models.BooleanField(
        default=False,
        editable=False,
        verbose_name="Kichik nusxa tozalangan",
        help_text="Thumbnail diskdan o'chirilgan; original Telegramda saqlanib qolgan.",
    )
    label = models.CharField(
        max_length=8, choices=Label.choices, verbose_name="Turi"
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")

    class Meta:
        verbose_name = "Natija rasmi"
        verbose_name_plural = "Natija rasmlari"
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["user", "-submitted_at"]),
            models.Index(fields=["-submitted_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.get_label_display()}"
