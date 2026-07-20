from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Staff(User):
    """
    Proxy over Django's auth user, so the CRM login accounts show up as
    "Xodimlar" instead of a page called "Users" sitting next to the customers
    and reading like it means them.
    """

    class Meta:
        proxy = True
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"


class SellerProfile(models.Model):
    """
    Links a Django auth user (a seller/admin who works in the CRM) to their
    Telegram account, so the bot can attribute referral registrations to them
    and the CRM can render their personal invite link.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seller_profile",
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        db_index=True,
        help_text="Sotuvchining Telegram ID raqami (referal havola uchun).",
    )
    display_name = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sotuvchi sozlamasi"
        verbose_name_plural = "Sotuvchi sozlamalari"

    @property
    def invite_link(self) -> str:
        username = getattr(settings, "BOT_USERNAME", "RealBeautyBot")
        return f"https://t.me/{username}?start=ref_{self.telegram_id}"

    def __str__(self) -> str:
        return self.display_name or (self.user.get_username())


class TelegramUser(models.Model):
    """Registered bot user."""

    class FaceCondition(models.TextChoices):
        DRY = "dry", "Quruq"
        OILY = "oily", "Yog'li"
        COMBINED = "combined", "Aralash"
        NORMAL = "normal", "Normal"
        SENSITIVE = "sensitive", "Sezgir"

    class RegistrationSource(models.TextChoices):
        SELF = "self", "O'zi ro'yxatdan o'tgan"
        ADMIN = "admin", "Admin yordamida"
        APP = "app", "Mobil ilova"

    class RegistrationStatus(models.TextChoices):
        PENDING = "pending", "To'ldirilishi kerak"
        COMPLETED = "completed", "To'ldirilgan"

    # Empty until the customer opens the bot. Staff add customers by name and
    # phone; the bot fills this in on /start by matching the phone number.
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name="Telegram ID",
    )
    username = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Telegram username"
    )
    full_name = models.CharField(max_length=256, blank=True, verbose_name="To'liq ism")
    birth_date = models.DateField(
        null=True, blank=True, verbose_name="Tug'ilgan sana"
    )
    phone_number = models.CharField(
        max_length=20, blank=True, verbose_name="Telefon raqami"
    )
    # Last 9 digits of phone_number, kept in sync by save(). Staff type
    # "+998 90 123 45 67" while Telegram reports "998901234567", so the raw
    # strings never compare equal — this column is what we actually match on.
    phone_tail = models.CharField(
        max_length=9, blank=True, db_index=True, editable=False
    )
    face_condition = models.CharField(
        max_length=20,
        choices=FaceCondition.choices,
        blank=True,
        verbose_name="Teri turi",
    )
    photo = models.ImageField(
        upload_to="user_photos/", blank=True, null=True, verbose_name="Rasm"
    )
    products = models.ManyToManyField(
        "products.Product",
        blank=True,
        through="UserProduct",
        verbose_name="Mahsulotlar",
    )
    registered_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals",
    )
    referred_by_seller = models.ForeignKey(
        SellerProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referred_users",
        verbose_name="Referal sotuvchi",
    )
    source = models.CharField(
        max_length=10,
        choices=RegistrationSource.choices,
        default=RegistrationSource.SELF,
    )
    registration_status = models.CharField(
        max_length=12,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.PENDING,
        verbose_name="Ro'yxat holati",
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan sana")

    class Meta:
        verbose_name = "Xaridor"
        verbose_name_plural = "Xaridorlar"

    def save(self, *args, **kwargs) -> None:
        self.phone_tail = self.phone_tail_of(self.phone_number)
        if "update_fields" in kwargs and kwargs["update_fields"] is not None:
            fields = set(kwargs["update_fields"])
            if "phone_number" in fields:
                fields.add("phone_tail")
                kwargs["update_fields"] = fields
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.username:
            return f"{self.full_name or 'Ismsiz'} (@{self.username})"
        return self.full_name or self.phone_number or f"#{self.pk}"

    @property
    def is_linked(self) -> bool:
        """True once the customer has opened the bot and we know their chat."""
        return self.telegram_id is not None

    @staticmethod
    def phone_tail_of(phone: str | None) -> str:
        """
        Last 9 digits of a phone number — the part that identifies a subscriber
        regardless of how it was typed (+998 90 123-45-67, 909 1234567, …).
        """
        digits = "".join(ch for ch in (phone or "") if ch.isdigit())
        return digits[-9:] if len(digits) >= 9 else ""

    @staticmethod
    def normalize_phone(phone: str | None) -> str | None:
        """
        Canonical +998XXXXXXXXX form, or None if this cannot be a phone number.

        Customers type their number every imaginable way and Telegram hands
        contacts over with no leading +, so what gets stored is settled here
        rather than at each call site.
        """
        digits = "".join(ch for ch in (phone or "") if ch.isdigit())
        if len(digits) == 9:  # 901234567 — local, assume Uzbekistan
            digits = f"998{digits}"
        if not 11 <= len(digits) <= 15:  # E.164 bounds, minus implausibly short
            return None
        return f"+{digits}"

    @property
    def is_birthday_today(self) -> bool:
        if not self.birth_date:
            return False
        today = timezone.now().date()
        return (
            self.birth_date.day == today.day
            and self.birth_date.month == today.month
        )


class AppUserManager(models.Manager):
    """Keeps the app-users page showing only rows the mobile app created."""

    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .filter(source=TelegramUser.RegistrationSource.APP)
        )


class AppUser(TelegramUser):
    """
    Proxy over the customer table, so people who signed up in the Flutter app
    get their own menu item instead of being something you have to remember to
    filter for on the (much busier) "Xaridorlar" page.

    Same rows, same table — "Xaridorlar" still lists everyone, this page is the
    app slice of it.
    """

    objects = AppUserManager()

    class Meta:
        proxy = True
        verbose_name = "App foydalanuvchisi"
        verbose_name_plural = "App foydalanuvchilari"


class UserProduct(models.Model):
    """Through model tracking when a user bought a product."""

    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi"
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, verbose_name="Mahsulot"
    )
    purchased_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Sotib olingan sana"
    )

    # Track campaign state for this purchase
    week1_sent = models.BooleanField(default=False, verbose_name="1-hafta yuborilgan")
    week2_sent = models.BooleanField(default=False, verbose_name="2-hafta yuborilgan")

    class Meta:
        unique_together = ("user", "product")
        verbose_name = "Sotib olingan mahsulot"
        verbose_name_plural = "Sotib olingan mahsulotlar"

    def __str__(self) -> str:
        return f"{self.user.full_name} — {self.product.name}"
