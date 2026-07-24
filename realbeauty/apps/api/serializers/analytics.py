from __future__ import annotations

from rest_framework import serializers

from apps.analytics.models import ProgressPhoto, SkinQuizResult, UserFeedback


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = [
            "id",
            "user",
            "product",
            "week",
            "rating",
            "text",
            "submitted_at",
            "admin_reply",
            "reply_sent",
        ]
        read_only_fields = [
            "user",
            "product",
            "week",
            "rating",
            "text",
            "submitted_at",
            "reply_sent",
        ]


class SkinQuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkinQuizResult
        fields = [
            "id",
            "user",
            "skin_type",
            "answers",
            "recommendation_keys",
            "language",
            "created_at",
        ]


class ProgressPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressPhoto
        fields = [
            "id",
            "user",
            "product",
            "file_id",
            "thumbnail",
            "thumbnail_purged",
            "label",
            "submitted_at",
        ]
