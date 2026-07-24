from __future__ import annotations

import logging

from rest_framework import mixins, viewsets

from apps.analytics.models import ProgressPhoto, SkinQuizResult, UserFeedback
from apps.api.pagination import DefaultPagination
from apps.api.permissions import ModelPermissions
from apps.api.serializers.analytics import (
    ProgressPhotoSerializer,
    SkinQuizResultSerializer,
    UserFeedbackSerializer,
)

logger = logging.getLogger(__name__)


class UserFeedbackViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = UserFeedback.objects.select_related("user", "product").all()
    serializer_class = UserFeedbackSerializer
    permission_classes = [ModelPermissions]
    pagination_class = DefaultPagination
    filterset_fields = ["week", "rating", "product"]
    search_fields = ["user__full_name", "text"]
    ordering_fields = ["submitted_at"]

    def perform_update(self, serializer):
        from core.telegram import TelegramError, send_message

        instance = serializer.instance
        send_now = bool(serializer.validated_data.get("admin_reply")) and (
            "admin_reply" in serializer.validated_data
            and serializer.validated_data["admin_reply"] != instance.admin_reply
        )
        instance = serializer.save()
        if not send_now or not instance.user.telegram_id:
            return
        try:
            send_message(
                instance.user.telegram_id,
                instance.admin_reply,
                reply_button=("✍️ Javob yozish", "support_reply"),
            )
        except TelegramError as exc:
            logger.warning("Feedback reply to %s failed: %s", instance.user.telegram_id, exc)
            return
        instance.reply_sent = True
        instance.save(update_fields=["reply_sent"])


class SkinQuizResultViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SkinQuizResult.objects.select_related("user").all()
    serializer_class = SkinQuizResultSerializer
    permission_classes = [ModelPermissions]
    pagination_class = DefaultPagination
    filterset_fields = ["skin_type", "language"]
    search_fields = ["user__full_name", "user__phone_number"]
    ordering_fields = ["created_at"]


class ProgressPhotoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ProgressPhoto.objects.select_related("user", "product").all()
    serializer_class = ProgressPhotoSerializer
    permission_classes = [ModelPermissions]
    pagination_class = DefaultPagination
    filterset_fields = ["label", "product"]
    search_fields = ["user__full_name", "user__phone_number"]
    ordering_fields = ["submitted_at"]
