from __future__ import annotations

from rest_framework import serializers

from apps.loyalty.models import (
    LoyaltyAccount,
    LoyaltySettings,
    PointsTransaction,
    Reward,
    RewardRedemption,
)


class LoyaltySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltySettings
        fields = [
            "is_enabled",
            "points_registration",
            "points_purchase",
            "points_feedback",
            "points_progress",
            "points_referral",
            "points_birthday",
            "points_quiz",
            "bronze_cashback",
            "silver_from",
            "silver_cashback",
            "gold_from",
            "gold_cashback",
            "platinum_from",
            "platinum_cashback",
        ]

    def validate(self, attrs: dict) -> dict:
        def get(name):
            return attrs.get(name, getattr(self.instance, name, None))

        silver, gold, platinum = get("silver_from"), get("gold_from"), get("platinum_from")
        if not (0 < silver < gold < platinum):
            raise serializers.ValidationError(
                "Darajalar ortib borishi kerak: Kumush < Oltin < Platina "
                f"(hozir: {silver} / {gold} / {platinum})."
            )
        return attrs


class LoyaltyAccountSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = LoyaltyAccount
        fields = [
            "id",
            "user",
            "user_name",
            "balance",
            "lifetime_points",
            "tier",
            "updated_at",
        ]
        read_only_fields = fields


class LoyaltyAdjustSerializer(serializers.Serializer):
    adjustment = serializers.IntegerField()
    note = serializers.CharField(required=False, allow_blank=True, max_length=200)


class PointsTransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = PointsTransaction
        fields = [
            "id",
            "user",
            "user_name",
            "points",
            "reason",
            "reference",
            "note",
            "created_at",
        ]
        read_only_fields = fields


class RewardSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)
    claimed = serializers.IntegerField(source="redemptions.count", read_only=True)

    class Meta:
        model = Reward
        fields = [
            "id",
            "title",
            "title_ru",
            "title_en",
            "description",
            "description_ru",
            "description_en",
            "cost_points",
            "code_prefix",
            "stock",
            "is_active",
            "created_at",
            "is_available",
            "claimed",
        ]
        read_only_fields = ["created_at"]


class RewardRedemptionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    reward_title = serializers.CharField(source="reward.title", read_only=True)

    class Meta:
        model = RewardRedemption
        fields = [
            "id",
            "user",
            "user_name",
            "reward",
            "reward_title",
            "code",
            "points_spent",
            "is_used",
            "used_at",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "reward",
            "code",
            "points_spent",
            "used_at",
            "created_at",
        ]
