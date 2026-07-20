from __future__ import annotations

import re

from django import forms
from django.contrib import admin, messages
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from unfold.decorators import action

from core.admin import RBModelAdmin, yes_no_filter

from .models import Broadcast, CampaignLog, MessageTemplate


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


class BroadcastForm(forms.ModelForm):
    class Meta:
        model = Broadcast
        fields = "__all__"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        from apps.users.models import TelegramUser

        # A free-text skin type would never match the stored choice values;
        # offer the same options the customer picked from.
        self.fields["skin_condition"] = forms.ChoiceField(
            required=False,
            label="Teri turi",
            choices=[("", "—")] + list(TelegramUser.FaceCondition.choices),
            help_text="«Teri turi bo'yicha» tanlansagina ishlaydi.",
        )

    def clean(self):
        cleaned = super().clean()
        audience = cleaned.get("audience")
        if audience == Broadcast.Audience.BY_SKIN and not cleaned.get("skin_condition"):
            self.add_error("skin_condition", "Teri turini tanlang.")
        if audience == Broadcast.Audience.BY_PRODUCT and not cleaned.get("product"):
            self.add_error("product", "Mahsulotni tanlang.")
        return cleaned


@admin.register(Broadcast)
class BroadcastAdmin(RBModelAdmin):
    form = BroadcastForm
    """
    Compose-and-send announcements: seminars, new arrivals, flash sales.

    Two guard rails, because a send cannot be recalled: "menga test" delivers
    the exact message to the composer first, and "hammaga yuborish" routes
    through a confirmation page showing the real recipient count.
    """

    list_display = ["title", "audience_label", "status_badge", "reach", "created_at"]
    list_display_links = ["title"]
    list_filter = ["status", "audience"]
    search_fields = ["title", "body"]
    readonly_fields = ["status", "delivery_summary", "created_at"]
    actions_detail = ["action_test_to_me", "action_send_now"]

    fieldsets = (
        (
            "Xabar",
            {
                "fields": ["title", "body", "photo"],
                "description": "Avval matnni yozing, «Saqlash»dan so'ng test "
                "qilib, keyin yuboring.",
            },
        ),
        (
            "Kimlarga",
            {"fields": ["audience", "skin_condition", "product"]},
        ),
        ("Holat", {"fields": ["status", "delivery_summary", "created_at"]}),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        # Once sent, the content is frozen — editing it would misrepresent what
        # customers actually received.
        if obj and obj.status in (
            Broadcast.Status.SENDING,
            Broadcast.Status.SENT,
        ):
            fields += ["title", "body", "photo", "audience", "skin_condition", "product"]
        return fields

    @admin.display(description="Kimlarga")
    def audience_label(self, obj: Broadcast) -> str:
        base = obj.get_audience_display().split(" (")[0]
        if obj.audience == Broadcast.Audience.BY_SKIN and obj.skin_condition:
            return f"{base}: {obj.skin_condition}"
        if obj.audience == Broadcast.Audience.BY_PRODUCT and obj.product:
            return f"{base}: {obj.product.name}"
        return base

    @admin.display(description="Holat")
    def status_badge(self, obj: Broadcast) -> str:
        colors = {
            Broadcast.Status.DRAFT: ("#6b7280", "📝 Qoralama"),
            Broadcast.Status.SENDING: ("#f59e0b", "⏳ Yuborilmoqda…"),
            Broadcast.Status.SENT: ("#059669", "✅ Yuborildi"),
            Broadcast.Status.FAILED: ("#dc2626", "❌ Xato"),
        }
        color, label = colors.get(obj.status, ("#6b7280", obj.status))
        return format_html('<span style="color:{};font-weight:600">{}</span>', color, label)

    @admin.display(description="Yetib bordi")
    def reach(self, obj: Broadcast) -> str:
        if obj.status == Broadcast.Status.SENT:
            out = f"{obj.sent_count} ta"
            if obj.failed_count:
                out += f" ({obj.failed_count} yetmadi)"
            return out
        return "—"

    @admin.display(description="Yuborish natijasi")
    def delivery_summary(self, obj: Broadcast) -> str:
        if obj.pk is None:
            return "—"
        if obj.status == Broadcast.Status.DRAFT:
            count = obj.recipients().count()
            return format_html(
                'Hozircha yuborilmagan. <b>{}</b> ta xaridorga yetib boradi.', count
            )
        if obj.status == Broadcast.Status.SENDING:
            return "⏳ Yuborilmoqda… Sahifani biroz o'tib yangilang."
        if obj.status == Broadcast.Status.SENT:
            return format_html(
                "✅ {} ta yuborildi, {} ta yetmadi (bloklagan yoki botni "
                "o'chirgan).",
                obj.sent_count,
                obj.failed_count,
            )
        return "❌ Yuborishda xatolik. Qayta urinib ko'ring."

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # --- per-object actions -------------------------------------------------

    @action(description="✍️ Menga test yuborish")
    def action_test_to_me(self, request, object_id):
        from apps.users.models import SellerProfile
        from tasks.broadcast import send_test

        profile = SellerProfile.objects.filter(user=request.user).first()
        if profile is None or not profile.telegram_id:
            self.message_user(
                request,
                "Sizga test yuborish uchun Xodimlar → o'zingizga Telegram ID "
                "kiriting.",
                level=messages.ERROR,
            )
            return redirect(request.path.replace("action_test_to_me/", ""))

        try:
            ok, error = send_test(int(object_id), profile.telegram_id)
        except Exception as exc:  # noqa: BLE001
            ok, error = False, str(exc)
        if ok:
            self.message_user(request, "Test xabar sizga yuborildi ✅ — botni tekshiring.")
        else:
            self.message_user(
                request, f"Test yuborilmadi: {error}", level=messages.ERROR
            )
        return redirect(request.path.replace("action_test_to_me/", ""))

    @action(description="📣 Hammaga yuborish")
    def action_send_now(self, request, object_id):
        from tasks.broadcast import send_broadcast

        broadcast = Broadcast.objects.get(pk=object_id)
        change_url = reverse(
            "admin:campaigns_broadcast_change", args=[object_id]
        )

        if broadcast.status in (Broadcast.Status.SENDING, Broadcast.Status.SENT):
            self.message_user(
                request, "Bu e'lon allaqachon yuborilgan.", level=messages.WARNING
            )
            return redirect(change_url)

        # POST from the confirmation page = go. GET = show the page first.
        if request.method == "POST" and request.POST.get("confirm") == "yes":
            send_broadcast.delay(broadcast.pk)
            self.message_user(
                request,
                "📣 Yuborish boshlandi. Bir necha daqiqada holat «Yuborildi» "
                "bo'ladi — sahifani yangilab turing.",
            )
            return redirect(change_url)

        count = broadcast.recipients().count()
        return render(
            request,
            "admin/campaigns/broadcast_confirm.html",
            {
                "broadcast": broadcast,
                "count": count,
                "title": "E'lonni yuborish",
                "back_url": change_url,
                **self.admin_site.each_context(request),
            },
        )
