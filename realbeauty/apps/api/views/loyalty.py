from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.pagination import DefaultPagination
from apps.api.permissions import IsSuperUser, ModelPermissions
from apps.api.serializers.loyalty import (
    LoyaltyAccountSerializer,
    LoyaltyAdjustSerializer,
    LoyaltySettingsSerializer,
    PointsTransactionSerializer,
    RewardRedemptionSerializer,
    RewardSerializer,
)
from apps.loyalty.models import LoyaltyAccount, LoyaltySettings, PointsTransaction, Reward, RewardRedemption
from apps.loyalty.services import award, spend


class LoyaltySettingsView(APIView):
    permission_classes = [IsSuperUser]

    @extend_schema(responses=LoyaltySettingsSerializer)
    def get(self, request):
        return Response(LoyaltySettingsSerializer(LoyaltySettings.get()).data)

    @extend_schema(request=LoyaltySettingsSerializer, responses=LoyaltySettingsSerializer)
    def patch(self, request):
        settings = LoyaltySettings.get()
        serializer = LoyaltySettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoyaltyAccountViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = LoyaltyAccount.objects.select_related("user").all()
    serializer_class = LoyaltyAccountSerializer
    permission_classes = [IsSuperUser]
    pagination_class = DefaultPagination
    filterset_fields = ["tier"]
    search_fields = ["user__full_name", "user__phone_number", "user__username"]
    ordering_fields = ["lifetime_points", "balance"]

    @extend_schema(request=LoyaltyAdjustSerializer, responses=LoyaltyAccountSerializer)
    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        """Manual correction — always routed through services.award/spend, never a raw write."""
        account = self.get_object()
        serializer = LoyaltyAdjustSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delta = serializer.validated_data["adjustment"]
        note = serializer.validated_data.get("note", "")

        if delta > 0:
            award(account.user, PointsTransaction.Reason.MANUAL, points=delta, note=note, notify=False)
        elif delta < 0:
            ok = spend(account.user, -delta, reason=PointsTransaction.Reason.MANUAL, note=note)
            if not ok:
                return Response(
                    {"detail": "Balans yetarli emas — ayirib bo'lmadi."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        account.refresh_from_db()
        return Response(LoyaltyAccountSerializer(account).data)


class PointsTransactionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = PointsTransaction.objects.select_related("user").all()
    serializer_class = PointsTransactionSerializer
    permission_classes = [IsSuperUser]
    pagination_class = DefaultPagination
    filterset_fields = ["reason", "user"]
    search_fields = ["user__full_name", "user__phone_number", "note"]
    ordering_fields = ["created_at"]


class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [IsSuperUser]
    pagination_class = DefaultPagination
    filterset_fields = ["is_active"]
    search_fields = ["title", "description"]
    ordering_fields = ["cost_points"]


class RewardRedemptionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """The till-facing page — Seller group can view/mark-used, never create/delete."""

    queryset = RewardRedemption.objects.select_related("user", "reward").all()
    serializer_class = RewardRedemptionSerializer
    permission_classes = [ModelPermissions]
    pagination_class = DefaultPagination
    filterset_fields = ["is_used"]
    search_fields = ["code", "user__full_name", "user__phone_number"]
    ordering_fields = ["created_at"]
