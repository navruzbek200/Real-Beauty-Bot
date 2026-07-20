from __future__ import annotations

import logging

from django import forms
from django.contrib import admin, messages
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.timezone import localtime
from core.admin import RBModelAdmin, yes_no_filter

from core.telegram import TelegramError, send_message

from .models import SupportMessage, SupportThread

logger = logging.getLogger(__name__)


class SupportThreadForm(forms.ModelForm):
    """Adds a write-only reply box on top of the thread's own fields."""

    reply = forms.CharField(
        label="Javob yozish",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Mijozga javob…"}),
        help_text="Saqlaganingizda matn darhol botda mijozga yuboriladi.",
    )

    class Meta:
        model = SupportThread
        fields = ["status"]


@admin.register(SupportThread)
class SupportThreadAdmin(RBModelAdmin):
    form = SupportThreadForm
    list_display = ["user", "subject", "preview", "state_badge", "last_message_at"]
    list_filter = [
        yes_no_filter(
            "awaiting_reply", "Javob kerakmi", "Javob kutmoqda", "Javob berilgan"
        ),
        "status",
    ]
    search_fields = ["user__full_name", "user__username", "subject", "messages__text"]
    date_hierarchy = "last_message_at"
    list_per_page = 30
    list_display_links = ["user", "subject"]
    fields = ["conversation", "reply", "status"]
    readonly_fields = ["conversation"]

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).select_related("user")

    @admin.display(description="Oxirgi xabar")
    def preview(self, obj: SupportThread) -> str:
        last = obj.messages.last()
        if last is None:
            return "—"
        arrow = "←" if last.direction == SupportMessage.Direction.IN else "→"
        text = last.text or "📷 rasm"
        return f"{arrow} {text[:60]}"

    @admin.display(description="Holat")
    def state_badge(self, obj: SupportThread) -> str:
        if obj.awaiting_reply:
            return format_html(
                '<span style="color:#dc2626;font-weight:600">🔴 Javob kutmoqda</span>'
            )
        if obj.status == SupportThread.Status.CLOSED:
            return format_html('<span style="color:#9ca3af">✔ Yopilgan</span>')
        return format_html('<span style="color:#059669">✅ Javob berildi</span>')

    @admin.display(description="Yozishmalar")
    def conversation(self, obj: SupportThread) -> str:
        if obj.pk is None:
            return "—"
        bubbles = []
        for msg in obj.messages.select_related("author"):
            incoming = msg.direction == SupportMessage.Direction.IN
            if incoming:
                who = obj.user.full_name or str(obj.user.telegram_id)
            else:
                who = str(msg.author) if msg.author else "Admin"

            body = format_html('<div style="white-space:pre-wrap">{}</div>', msg.text)
            if msg.photo_file_id:
                body = format_html(
                    '{}<a href="{}" target="_blank" '
                    'style="font-size:12px">📷 Rasmni ochish</a>',
                    body,
                    reverse("telegram_file", args=[msg.photo_file_id]),
                )
            if not msg.delivered:
                body = format_html(
                    '{}<div style="font-size:12px;color:#dc2626">'
                    "⚠️ Yuborilmadi: {}</div>",
                    body,
                    msg.error_detail,
                )
            bubbles.append(
                (
                    "flex-start" if incoming else "flex-end",
                    "#f3f4f6" if incoming else "#dbeafe",
                    who,
                    localtime(msg.created_at).strftime("%d.%m.%Y %H:%M"),
                    body,
                )
            )
        if not bubbles:
            return "—"
        return format_html(
            '<div style="max-height:460px;overflow-y:auto;padding:4px">{}</div>',
            format_html_join(
                "",
                '<div style="display:flex;justify-content:{};margin:6px 0">'
                '<div style="max-width:70%;background:{};border-radius:10px;'
                'padding:8px 12px">'
                '<div style="font-size:11px;color:#6b7280;margin-bottom:2px">'
                "{} · {}</div>{}</div></div>",
                bubbles,
            ),
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        reply = (form.cleaned_data.get("reply") or "").strip()
        if not reply:
            return

        message = SupportMessage(
            thread=obj,
            direction=SupportMessage.Direction.OUT,
            text=reply,
            author=request.user,
        )
        try:
            # The button drops the customer straight back into the support
            # flow — otherwise their typed follow-up hits the menu fallback.
            send_message(
                obj.user.telegram_id,
                reply,
                reply_button=("✍️ Javob yozish", "support_reply"),
            )
        except TelegramError as exc:
            message.delivered = False
            message.error_detail = str(exc)
            message.save()
            logger.warning("Support reply to %s failed: %s", obj.user.telegram_id, exc)
            messages.error(request, f"Javob yuborilmadi: {exc}")
            return

        message.save()
        obj.touch(from_user=False)
        messages.success(request, "Javob mijozga yuborildi ✅")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: SupportThread | None = None
    ) -> bool:
        return request.user.is_superuser
