from __future__ import annotations

from typing import Any

from django.db import models
from django.utils import timezone


class GlobalSettings(models.Model):
    """
    Singleton model — only one row allowed.
    All values are editable from admin panel.
    """

    # The timed check-ins used to live here as four fixed fields. They are now
    # rows in `campaigns.AutoMessage`, where the shop controls the wording, the
    # delay *and* its unit — see the 0009 migration, which carried the old
    # values over.
    birthday_discount_percent = models.PositiveSmallIntegerField(
        default=30,
        verbose_name="Tug'ilgan kun chegirmasi (%)",
        help_text="Tug'ilgan kun xabaridagi foiz. Xabar matnida {{ discount }} "
        "o'rniga shu raqam qo'yiladi.",
    )

    class Meta:
        verbose_name = "Umumiy sozlamalar"
        verbose_name_plural = "Umumiy sozlamalar"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def get(cls) -> "GlobalSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self) -> str:
        return "Umumiy sozlamalar"


class Discount(models.Model):
    """
    Dynamic, admin-editable discount/promotion shown to bot users via the
    "Chegirmalar" menu button.
    """

    title = models.CharField(max_length=128, verbose_name="Sarlavha")
    percent = models.PositiveSmallIntegerField(
        default=0, verbose_name="Chegirma foizi (%)"
    )
    description = models.TextField(blank=True, verbose_name="Tavsif")
    promo_code = models.CharField(max_length=64, blank=True, verbose_name="Promokod")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    valid_until = models.DateField(null=True, blank=True, verbose_name="Amal qilish muddati")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chegirma"
        verbose_name_plural = "Chegirmalar"
        ordering = ["-created_at"]

    @property
    def is_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.valid_until and self.valid_until < timezone.localdate():
            return False
        return True

    def __str__(self) -> str:
        return f"{self.title} — {self.percent}%"
