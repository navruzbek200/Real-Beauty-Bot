from __future__ import annotations

import re

from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from core.admin import RBModelAdmin, yes_no_filter

from .models import CampaignLog, MessageTemplate


@admin.register(MessageTemplate)
class MessageTemplateAdmin(RBModelAdmin):
    """
    The six automatic messages, one row each.

    They are a fixed set the bot sends at fixed moments, so this page is for
    editing wording only — adding a seventh or deleting one would just leave
    the bot with nothing to send.
    """

    list_display = ["when_sent", "preview", "active_badge", "updated_at"]
    list_display_links = ["when_sent"]
    list_filter = [
        yes_no_filter("is_active", "Yuborilishi", "Yuborilyapti", "O'chirilgan")
    ]
    search_fields = ["name", "body"]
    fields = ["template_type", "name", "body", "parse_mode", "is_active"]
    readonly_fields = ["template_type"]
    ordering = ["template_type"]

    @admin.display(description="Qachon yuboriladi", ordering="template_type")
    def when_sent(self, obj: MessageTemplate) -> str:
        return obj.get_template_type_display()

    @admin.display(description="Matn")
    def preview(self, obj: MessageTemplate) -> str:
        text = re.sub(r"<[^>]+>", "", obj.body).replace("\n", " ")
        return text[:90] + ("…" if len(text) > 90 else "")

    @admin.display(description="Holat")
    def active_badge(self, obj: MessageTemplate) -> str:
        if obj.is_active:
            return format_html(
                '<span style="color:#059669;font-weight:600">✅ Yuborilyapti</span>'
            )
        return format_html('<span style="color:#9ca3af">⏸ O\'chirilgan</span>')

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: MessageTemplate | None = None
    ) -> bool:
        return False

    # Sellers must not see or edit templates
    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser

    def has_view_permission(
        self, request: HttpRequest, obj: MessageTemplate | None = None
    ) -> bool:
        return request.user.is_superuser


@admin.register(CampaignLog)
class CampaignLogAdmin(RBModelAdmin):
    list_display = ["user", "template", "sent_at", "result"]
    list_filter = [
        yes_no_filter("success", "Yetkazilganmi", "Yetkazilgan", "Yetkazilmagan"),
        "template__template_type",
    ]
    search_fields = ["user__full_name", "user__phone_number"]
    readonly_fields = ["user", "template", "sent_at", "success", "error_detail"]
    date_hierarchy = "sent_at"
    list_per_page = 30

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).select_related("user", "template")

    @admin.display(description="Natija")
    def result(self, obj: CampaignLog) -> str:
        if obj.success:
            return format_html('<span style="color:#059669">✅ Yetkazildi</span>')
        # The reason matters more than the flag: usually "bot was blocked".
        return format_html(
            '<span style="color:#dc2626">❌ Yetkazilmadi</span>'
            '<div style="font-size:11px;color:#6b7280">{}</div>',
            obj.error_detail[:80],
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: CampaignLog | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: CampaignLog | None = None
    ) -> bool:
        return request.user.is_superuser

    # Sellers must not see logs
    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser

    def has_view_permission(
        self, request: HttpRequest, obj: CampaignLog | None = None
    ) -> bool:
        return request.user.is_superuser
