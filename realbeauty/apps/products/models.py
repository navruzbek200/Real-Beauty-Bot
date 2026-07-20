from __future__ import annotations

from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=256, verbose_name="Nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    photo = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name="Rasm (ixtiyoriy)",
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self) -> str:
        return self.name


class ProductTutorialStep(models.Model):
    """
    One tutorial step of a product: an inline button in the bot that plays a
    short "how to use" video. Everything (button text, message, video) is
    managed right inside the product — no separate video library.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="tutorial_steps",
        verbose_name="Mahsulot",
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Ketma-ketlik",
        help_text="Tugmalar tartibi: 1, 2, 3 ... (kichik raqam yuqorida turadi).",
    )
    button_label = models.CharField(
        max_length=64,
        verbose_name="Tugma matni",
        help_text="Botda ko'rinadigan tugma, masalan: «1-qadam: Tozalash».",
    )
    intro_text = models.TextField(
        verbose_name="Video oldidan matn",
        help_text="Video yuborilishidan oldin ko'rsatiladigan qisqa izoh.",
    )
    video_file = models.FileField(
        upload_to="videos/",
        blank=True,
        null=True,
        verbose_name="Video (ixtiyoriy)",
        help_text="Video yuklang. Yuklamasangiz bot «tez orada» deb yozadi.",
    )
    # Filled automatically by the bot after the first send (reuse, no re-upload).
    video_file_id = models.CharField(max_length=512, blank=True, editable=False)
    protect_content = models.BooleanField(
        default=True,
        verbose_name="Himoya (ulashish/saqlashni taqiqlash)",
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Qo'llanma qadami"
        verbose_name_plural = "Qo'llanma qadamlari"

    @property
    def has_video(self) -> bool:
        return bool(self.video_file_id or (self.video_file and self.video_file.name))

    def __str__(self) -> str:
        return f"{self.product.name} — {self.order}: {self.button_label}"
