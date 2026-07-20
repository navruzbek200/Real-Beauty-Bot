from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class SupportThread(models.Model):
    """
    One ongoing conversation between a bot user and the shop.

    A user has at most one open thread at a time: new messages land in the open
    thread, and a closed thread is reopened if the user writes again.
    """

    class Status(models.TextChoices):
        NEW = "new", "Yangi"
        ANSWERED = "answered", "Javob berildi"
        CLOSED = "closed", "Yopilgan"

    user = models.ForeignKey(
        "users.TelegramUser",
        on_delete=models.CASCADE,
        related_name="support_threads",
        verbose_name="Foydalanuvchi",
    )
    subject = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Mavzu",
        help_text="Foydalanuvchining birinchi xabaridan avtomatik olinadi.",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
        verbose_name="Holat",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ochilgan vaqt")
    last_message_at = models.DateTimeField(
        default=timezone.now, db_index=True, verbose_name="Oxirgi xabar"
    )
    # True while the newest message is from the user and nobody replied yet.
    awaiting_reply = models.BooleanField(
        default=True, db_index=True, verbose_name="Javob kutilmoqda"
    )

    class Meta:
        verbose_name = "Murojaat"
        verbose_name_plural = "Murojaatlar"
        ordering = ["-awaiting_reply", "-last_message_at"]
        indexes = [
            models.Index(fields=["-last_message_at"]),
            models.Index(fields=["status", "-last_message_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.subject or 'murojaat'}"

    def touch(self, *, from_user: bool) -> None:
        """Update thread state after a new message is appended."""
        self.last_message_at = timezone.now()
        self.awaiting_reply = from_user
        # A user message (re)opens the thread; an admin message answers it.
        self.status = self.Status.NEW if from_user else self.Status.ANSWERED
        self.save(update_fields=["last_message_at", "awaiting_reply", "status"])


class SupportMessage(models.Model):
    """A single message inside a thread, in either direction."""

    class Direction(models.TextChoices):
        IN = "in", "Foydalanuvchidan"
        OUT = "out", "Admindan"

    thread = models.ForeignKey(
        SupportThread,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Murojaat",
    )
    direction = models.CharField(
        max_length=4, choices=Direction.choices, verbose_name="Yo'nalish"
    )
    text = models.TextField(blank=True, verbose_name="Matn")
    # Telegram file_id of a photo the user attached (no disk copy kept).
    photo_file_id = models.CharField(max_length=512, blank=True, editable=False)
    # Set for outgoing messages: which staff account wrote the reply.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Muallif",
    )
    delivered = models.BooleanField(
        default=True, editable=False, verbose_name="Yetkazildi"
    )
    error_detail = models.TextField(blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vaqt")

    class Meta:
        verbose_name = "Murojaat xabari"
        verbose_name_plural = "Murojaat xabarlari"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["thread", "created_at"])]

    def __str__(self) -> str:
        return f"{self.get_direction_display()}: {self.text[:40]}"
