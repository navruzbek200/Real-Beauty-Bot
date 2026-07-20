from __future__ import annotations

import logging

from django.contrib import admin, messages
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from core.admin import RBModelAdmin

from core.telegram import TelegramError, send_message

from .models import ProgressPhoto, UserFeedback

logger = logging.getLogger(__name__)


@admin.register(UserFeedback)
class UserFeedbackAdmin(RBModelAdmin):
    list_display = ["user", "product", "week", "rating", "replied_badge", "submitted_at"]
    list_filter = ["week", "rating", "product"]
    search_fields = ["user__full_name", "text"]
    readonly_fields = ["user", "product", "week", "rating", "text", "submitted_at"]
    fields = [
        "user",
        "product",
        "week",
        "rating",
        "text",
        "submitted_at",
        "admin_reply",
    ]
    date_hierarchy = "submitted_at"
    list_per_page = 30

    @admin.display(description="Javob")
    def replied_badge(self, obj: UserFeedback) -> str:
        if obj.reply_sent:
            return format_html('<span style="color:#059669">✅ Javob berildi</span>')
        return format_html('<span style="color:#9ca3af">—</span>')

    def save_model(self, request, obj, form, change):
        # If the admin typed a reply, send it to the customer via the bot.
        send_now = bool(obj.admin_reply) and "admin_reply" in form.changed_data
        super().save_model(request, obj, form, change)
        if not send_now:
            return
        if not obj.user.telegram_id:
            messages.error(request, "Mijoz hali botga ulanmagan — javob yuborilmadi.")
            return
        try:
            send_message(
                obj.user.telegram_id,
                obj.admin_reply,
                reply_button=("✍️ Javob yozish", "support_reply"),
            )
        except TelegramError as exc:
            logger.warning("Feedback reply to %s failed: %s", obj.user.telegram_id, exc)
            messages.error(request, f"Javob yuborilmadi: {exc}")
            return
        obj.reply_sent = True
        obj.save(update_fields=["reply_sent"])
        messages.success(request, "Javob mijozga yuborildi ✅")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: UserFeedback | None = None
    ) -> bool:
        return request.user.is_superuser


@admin.register(ProgressPhoto)
class ProgressPhotoAdmin(RBModelAdmin):
    list_display = ["preview", "user", "product", "label", "submitted_at"]
    list_display_links = ["preview", "user"]
    list_filter = ["label", "product"]
    search_fields = ["user__full_name", "user__phone_number"]
    readonly_fields = ["user", "product", "label", "big_preview", "submitted_at"]
    fields = ["big_preview", "user", "product", "label", "submitted_at"]
    date_hierarchy = "submitted_at"
    list_per_page = 24

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).select_related("user", "product")

    def _thumb_html(self, obj: ProgressPhoto, size: int) -> str:
        if obj.thumbnail and not obj.thumbnail_purged:
            img = format_html(
                '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;'
                'border-radius:6px" loading="lazy">',
                obj.thumbnail.url,
                size,
                size,
            )
        elif obj.file_id:
            img = format_html(
                '<span style="display:inline-flex;align-items:center;'
                "justify-content:center;width:{}px;height:{}px;background:#f3f4f6;"
                'border-radius:6px;font-size:11px;color:#6b7280">Telegramda</span>',
                size,
                size,
            )
        else:
            return "—"
        if not obj.file_id:
            return img
        # Click through to the full-size original, still on Telegram's servers.
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            reverse("telegram_file", args=[obj.file_id]),
            img,
        )

    @admin.display(description="Rasm")
    def preview(self, obj: ProgressPhoto) -> str:
        return self._thumb_html(obj, 72)

    @admin.display(description="Rasm (asl nusxa uchun bosing)")
    def big_preview(self, obj: ProgressPhoto) -> str:
        return self._thumb_html(obj, 320)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: ProgressPhoto | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: ProgressPhoto | None = None
    ) -> bool:
        return request.user.is_superuser
