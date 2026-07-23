from __future__ import annotations

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from core.admin import RBModelAdmin, yes_no_filter

from .models import (
    LoyaltyAccount,
    LoyaltySettings,
    PointsTransaction,
    Reward,
    RewardRedemption,
)
from .services import award, spend


@admin.register(LoyaltySettings)
class LoyaltySettingsAdmin(RBModelAdmin):
    """
    The whole points economy on one form.

    A changelist holding exactly one row makes the sidebar entry look broken,
    so the changelist forwards straight to the form.
    """

    fieldsets = (
        (
            "Bonus dasturi",
            {
                "fields": ["is_enabled"],
                "description": "O'chirilsa botdagi «💎 Bonuslarim» bo'limi "
                "ishlamaydi va yangi ball yig'ilmaydi.",
            },
        ),
        (
            "Mijoz qaysi ish uchun necha ball oladi",
            {
                "fields": [
                    "points_registration",
                    "points_purchase",
                    "points_feedback",
                    "points_progress",
                    "points_referral",
                    "points_birthday",
                    "points_quiz",
                ],
                "description": "0 qilib qo'ysangiz — o'sha ish uchun ball "
                "berilmaydi.",
            },
        ),
        (
            "Darajalar va keshbek",
            {
                "fields": [
                    "bronze_cashback",
                    "silver_from",
                    "silver_cashback",
                    "gold_from",
                    "gold_cashback",
                    "platinum_from",
                    "platinum_cashback",
                ],
                "description": "Daraja mijoz JAMI yig'gan ballga qarab "
                "belgilanadi — sovg'aga ball sarflasa daraja pasaymaydi.",
            },
        ),
    )

    def changelist_view(self, request: HttpRequest, extra_context=None) -> HttpResponse:
        # The redirect skips the stock changelist (and its permission check),
        # so the check has to happen here.
        if not self.has_view_permission(request):
            raise PermissionDenied
        settings = LoyaltySettings.get()
        return HttpResponseRedirect(
            reverse("admin:loyalty_loyaltysettings_change", args=[settings.pk])
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.is_superuser

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.is_superuser


class PointsAdjustmentForm(forms.ModelForm):
    """Manual correction: a signed number and a reason, nothing else."""

    adjustment = forms.IntegerField(
        required=False,
        label="Ballni qo'lda o'zgartirish",
        help_text="Masalan: 100 (qo'shish) yoki -50 (ayirish). Bo'sh "
        "qoldirsangiz hech nima o'zgarmaydi.",
    )
    adjustment_note = forms.CharField(
        required=False, max_length=200, label="Izoh"
    )

    class Meta:
        model = LoyaltyAccount
        fields: list[str] = []


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(RBModelAdmin):
    form = PointsAdjustmentForm
    list_display = ["user", "balance", "lifetime_points", "tier_badge", "updated_at"]
    list_display_links = ["user"]
    list_filter = ["tier"]
    search_fields = ["user__full_name", "user__phone_number", "user__username"]
    readonly_fields = ["user", "balance", "lifetime_points", "tier"]
    list_per_page = 30

    fieldsets = (
        ("Hisob", {"fields": ["user", "balance", "lifetime_points", "tier"]}),
        (
            "Qo'lda tuzatish",
            {
                "fields": ["adjustment", "adjustment_note"],
                "description": "Do'konda berilgan sovg'a yoki xatoni tuzatish "
                "uchun. Har bir o'zgarish tarixda qoladi.",
            },
        ),
    )

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).select_related("user")

    @admin.display(description="Daraja", ordering="tier")
    def tier_badge(self, obj: LoyaltyAccount) -> str:
        colors = {
            LoyaltyAccount.Tier.BRONZE: "#a16207",
            LoyaltyAccount.Tier.SILVER: "#6b7280",
            LoyaltyAccount.Tier.GOLD: "#d97706",
            LoyaltyAccount.Tier.PLATINUM: "#0ea5e9",
        }
        return format_html(
            '<span style="color:{};font-weight:600">{}</span>',
            colors.get(obj.tier, "#6b7280"),
            obj.get_tier_display(),
        )

    def save_model(self, request, obj, form, change) -> None:
        """
        Apply the correction through the service, never by writing `balance`.

        Editing the number directly would leave the transaction log — the only
        record of why a balance is what it is — silently out of step with it.
        """
        delta = form.cleaned_data.get("adjustment") or 0
        note = form.cleaned_data.get("adjustment_note") or ""
        if delta > 0:
            award(
                obj.user,
                PointsTransaction.Reason.MANUAL,
                points=delta,
                note=note,
                notify=False,
            )
        elif delta < 0:
            if not spend(
                obj.user,
                -delta,
                reason=PointsTransaction.Reason.MANUAL,
                note=note,
            ):
                self.message_user(
                    request,
                    "Balans yetarli emas — ayirib bo'lmadi.",
                    level=messages.ERROR,
                )
                return
        if delta:
            self.message_user(request, f"Ball {delta:+d} ga o'zgartirildi.")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.is_superuser


@admin.register(PointsTransaction)
class PointsTransactionAdmin(RBModelAdmin):
    list_display = ["user", "points_badge", "reason", "note", "created_at"]
    list_filter = ["reason"]
    search_fields = ["user__full_name", "user__phone_number", "note"]
    readonly_fields = ["user", "points", "reason", "reference", "note", "created_at"]
    date_hierarchy = "created_at"
    list_per_page = 40

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).select_related("user")

    @admin.display(description="Ball", ordering="points")
    def points_badge(self, obj: PointsTransaction) -> str:
        color = "#059669" if obj.points > 0 else "#dc2626"
        # The sign is applied before format_html: it escapes its arguments into
        # SafeString, which no longer accepts a numeric format spec.
        return format_html(
            '<span style="color:{};font-weight:600">{}</span>',
            color,
            f"{obj.points:+d}",
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.is_superuser


@admin.register(Reward)
class RewardAdmin(RBModelAdmin):
    list_display = ["title", "cost_points", "stock_label", "claimed", "state_badge"]
    list_display_links = ["title"]
    list_filter = [yes_no_filter("is_active", "Holati", "Faol", "O'chirilgan")]
    search_fields = ["title", "description"]
    fieldsets = (
        (
            "Sovg'a",
            {
                "fields": ["title", "description", "cost_points", "code_prefix"],
                "description": "Mijoz ballga almashtirganda unga noyob "
                "promokod beriladi — do'konda shu kodni ko'rsatadi.",
            },
        ),
        (
            "Boshqa tillar (ixtiyoriy)",
            {
                "fields": ["title_ru", "title_en", "description_ru", "description_en"],
                "classes": ["collapse"],
            },
        ),
        ("Mavjudligi", {"fields": ["stock", "is_active"]}),
    )

    @admin.display(description="Qoldi")
    def stock_label(self, obj: Reward) -> str:
        return "∞" if obj.stock is None else f"{obj.stock} ta"

    @admin.display(description="Olingan")
    def claimed(self, obj: Reward) -> str:
        return f"{obj.redemptions.count()} ta"

    @admin.display(description="Holat")
    def state_badge(self, obj: Reward) -> str:
        if obj.is_available:
            return format_html(
                '<span style="color:#059669;font-weight:600">✅ Botda ko\'rinadi</span>'
            )
        if not obj.is_active:
            return format_html('<span style="color:#9ca3af">⏸ O\'chirilgan</span>')
        return format_html('<span style="color:#dc2626">📦 Tugagan</span>')

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.is_superuser


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(RBModelAdmin):
    """The codes customers are holding — the list the till checks against."""

    list_display = ["code", "user", "reward", "points_spent", "used_badge", "created_at"]
    list_display_links = ["code"]
    list_filter = [
        yes_no_filter("is_used", "Ishlatilganmi", "Ishlatilgan", "Kutilmoqda")
    ]
    search_fields = ["code", "user__full_name", "user__phone_number"]
    readonly_fields = ["user", "reward", "code", "points_spent", "created_at"]
    fields = ["code", "user", "reward", "points_spent", "is_used", "created_at"]
    date_hierarchy = "created_at"

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).select_related("user", "reward")

    @admin.display(description="Holat", ordering="is_used")
    def used_badge(self, obj: RewardRedemption) -> str:
        if obj.is_used:
            return format_html('<span style="color:#6b7280">✔ Ishlatilgan</span>')
        return format_html(
            '<span style="color:#059669;font-weight:600">🎟 Kutilmoqda</span>'
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
