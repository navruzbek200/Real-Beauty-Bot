"""
Customer orders placed from the Mini App.

Phase 1 of the shop's online-sales plan: the app captures the order (items,
delivery choice, address), the operator confirms it by phone, and payment
happens on delivery. No payment provider is involved yet — when the Click or
Payme merchant contract lands, a "paid" status slots into the same flow.

Prices are snapshotted onto the order lines: the shop re-prices products all
the time, and an order must forever read the way it was placed.
"""

from __future__ import annotations

from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "🆕 Yangi"
        CONFIRMED = "confirmed", "☎️ Tasdiqlangan"
        SHIPPED = "shipped", "🚚 Yo'lda"
        DELIVERED = "delivered", "✅ Yetkazildi"
        CANCELLED = "cancelled", "❌ Bekor qilingan"

    class Delivery(models.TextChoices):
        YANDEX = "yandex", "🚕 Yandeks (Toshkent bo'ylab)"
        BTS = "bts", "📦 BTS (viloyatlarga)"

    user = models.ForeignKey(
        "users.TelegramUser",
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Mijoz",
    )
    customer_name = models.CharField(max_length=256, verbose_name="Ism-familiya")
    phone_number = models.CharField(max_length=32, verbose_name="Telefon")
    delivery_method = models.CharField(
        max_length=16, choices=Delivery.choices, verbose_name="Yetkazish"
    )
    address = models.TextField(
        verbose_name="Manzil",
        help_text="Yandeks: ko'cha va uy. BTS: viloyat, shahar va filial.",
    )
    comment = models.TextField(blank=True, verbose_name="Izoh")
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
        verbose_name="Holat",
    )
    # Denormalized sum of the lines, in so'm — the number every list screen
    # shows, kept here so listing orders never needs an aggregate query.
    total = models.PositiveBigIntegerField(default=0, verbose_name="Jami (so'm)")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def __str__(self) -> str:
        return f"Buyurtma #{self.pk} — {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Buyurtma"
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
        verbose_name="Mahsulot",
    )
    # Snapshots: the line stays readable even if the product is renamed,
    # re-priced or deleted later.
    product_name = models.CharField(max_length=256, verbose_name="Nomi")
    price = models.PositiveBigIntegerField(verbose_name="Narxi (so'm)")
    quantity = models.PositiveSmallIntegerField(default=1, verbose_name="Soni")

    class Meta:
        verbose_name = "Buyurtma qatori"
        verbose_name_plural = "Buyurtma qatorlari"

    @property
    def subtotal(self) -> int:
        return self.price * self.quantity

    def __str__(self) -> str:
        return f"{self.product_name} × {self.quantity}"
