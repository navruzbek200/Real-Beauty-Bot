from __future__ import annotations

from rest_framework import serializers

from apps.bot_settings.models import Discount, GlobalSettings


class GlobalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSettings
        fields = ["birthday_discount_percent"]


class DiscountSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Discount
        fields = [
            "id",
            "title",
            "percent",
            "description",
            "promo_code",
            "is_active",
            "valid_until",
            "created_at",
            "is_valid",
        ]
        read_only_fields = ["created_at"]
