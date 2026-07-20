from __future__ import annotations

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.http import HttpRequest
from django.utils.html import format_html
from unfold.admin import TabularInline

from core.admin import RBModelAdmin, yes_no_filter

from .models import TelegramUser, UserProduct

# Registers the staff-account admin that replaces Django's stock user page.
from . import staff_admin  # noqa: F401,E402  (import for side effects)

# The "Groups" (permission sets) page is not needed for this simple shop —
# the staff page asks for a role instead. Login accounts live under "Xodimlar".
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


class UserProductInline(TabularInline):
    model = UserProduct
    extra = 1
    fields = ["product", "week1_sent", "week2_sent"]
    readonly_fields = ["week1_sent", "week2_sent"]
    verbose_name = "Sotib olingan mahsulot"
    verbose_name_plural = "Sotib olingan mahsulotlar"


class TelegramUserForm(forms.ModelForm):
    """
    Staff-facing customer card.

    Deliberately free of Telegram plumbing: whoever adds a customer at the
    counter knows their name and phone, never their numeric Telegram ID, so the
    bot resolves that itself when the customer opens it.
    """

    class Meta:
        model = TelegramUser
        fields = [
            "full_name",
            "phone_number",
            "username",
            "birth_date",
            "face_condition",
            "photo",
            "is_active",
        ]
        labels = {
            "full_name": "Ism-familiya",
            "phone_number": "Telefon raqami",
            "username": "Telegram username",
            "photo": "Rasm",
        }
        help_texts = {
            "phone_number": "Masalan: +998 90 123 45 67. "
            "Mijoz botga kirganda shu raqam orqali ulanadi.",
            "username": "Ixtiyoriy. Bilsangiz yozing (@ belgisiz) — ulanish tezlashadi.",
            "birth_date": "Ixtiyoriy. To'ldirsangiz, tug'ilgan kunida chegirma "
            "xabari avtomatik boradi.",
            "face_condition": "Ixtiyoriy.",
            "photo": "Ixtiyoriy — shart emas.",
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # A card with no name is useless to look up later; the model keeps the
        # field blankable because the bot creates rows before asking the name.
        self.fields["full_name"].required = True
        self.fields["phone_number"].required = True

    def clean_username(self) -> str:
        # Staff type "@name" out of habit; store it the way Telegram reports it.
        return (self.cleaned_data.get("username") or "").lstrip("@").strip()

    def clean_phone_number(self) -> str:
        phone = (self.cleaned_data.get("phone_number") or "").strip()
        if not phone:
            return phone
        tail = TelegramUser.phone_tail_of(phone)
        if not tail:
            raise forms.ValidationError(
                "Raqam to'liq emas — kamida 9 ta raqam bo'lishi kerak."
            )
        # Two cards with the same number would both match the customer on /start.
        clash = TelegramUser.objects.filter(phone_tail=tail)
        if self.instance.pk:
            clash = clash.exclude(pk=self.instance.pk)
        existing = clash.first()
        if existing is not None:
            raise forms.ValidationError(
                f"Bu raqam «{existing}» xaridorga biriktirilgan."
            )
        return phone


@admin.register(TelegramUser)
class TelegramUserAdmin(RBModelAdmin):
    form = TelegramUserForm
    list_display = [
        "full_name",
        "phone_number",
        "products_list",
        "link_badge",
        "created_at",
    ]
    list_filter = [
        yes_no_filter("is_active", "Xaridor holati", "Faol", "O'chirilgan"),
        "face_condition",
    ]
    search_fields = ["full_name", "username", "phone_number"]
    readonly_fields = ["created_at", "link_help"]
    inlines = [UserProductInline]
    date_hierarchy = "created_at"
    list_per_page = 25
    list_display_links = ["full_name"]

    def get_queryset(self, request: HttpRequest):
        return (
            super().get_queryset(request).prefetch_related("userproduct_set__product")
        )

    def get_fieldsets(self, request: HttpRequest, obj: TelegramUser | None = None):
        if obj is None:
            # Adding: only what the person at the counter actually knows.
            return (
                (
                    "Xaridor ma'lumotlari",
                    {
                        "fields": [
                            "full_name",
                            "phone_number",
                            "username",
                            "birth_date",
                            "face_condition",
                        ]
                    },
                ),
            )
        return (
            (
                "Xaridor ma'lumotlari",
                {
                    "fields": [
                        "full_name",
                        "phone_number",
                        "username",
                        "birth_date",
                        "face_condition",
                        "photo",
                    ]
                },
            ),
            ("Bot", {"fields": ["link_help", "is_active", "created_at"]}),
        )

    def save_model(self, request, obj, form, change):
        if not change:
            # Cards born in the CRM, not from the bot's own /start flow.
            obj.source = TelegramUser.RegistrationSource.ADMIN
        super().save_model(request, obj, form, change)

    @admin.display(description="Mahsulotlar")
    def products_list(self, obj: TelegramUser) -> str:
        names = [up.product.name for up in obj.userproduct_set.all()]
        return ", ".join(names) if names else "—"

    @admin.display(description="Bot")
    def link_badge(self, obj: TelegramUser) -> str:
        if obj.is_linked:
            return format_html('<span style="color:#059669">✅ Ulangan</span>')
        return format_html('<span style="color:#f59e0b">⏳ Botga kirmagan</span>')

    @admin.display(description="Bot bilan aloqa")
    def link_help(self, obj: TelegramUser) -> str:
        if obj.is_linked:
            return format_html(
                '<span style="color:#059669;font-weight:600">✅ Mijoz botga '
                "ulangan.</span> Xabarlar unga avtomatik boradi."
            )
        return format_html(
            '<span style="color:#f59e0b;font-weight:600">⏳ Mijoz hali botga '
            "kirmagan.</span><br>Unga bot havolasini yuboring. Mijoz botda "
            "telefon raqamini yuborgach, kartasi shu yerga o'zi ulanadi — "
            "qo'lda hech nima qilish shart emas."
        )

    def has_delete_permission(
        self, request: HttpRequest, obj: TelegramUser | None = None
    ) -> bool:
        return request.user.is_superuser
