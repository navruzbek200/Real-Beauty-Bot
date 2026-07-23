from __future__ import annotations

from django.apps import AppConfig


class LoyaltyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.loyalty"
    verbose_name = "Bonus dasturi"

    def ready(self) -> None:
        # Importing for the side effect of registering the signal receivers
        # that credit points when a purchase, review or photo lands.
        from apps.loyalty import signals  # noqa: F401
