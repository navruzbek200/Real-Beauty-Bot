from __future__ import annotations

from rest_framework import mixins, viewsets

from apps.api.pagination import DefaultPagination
from apps.api.permissions import ModelPermissions
from apps.api.serializers.orders import OrderSerializer
from apps.orders.models import Order


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    The «Buyurtmalar» page. Orders are created only by customers through the
    Mini App (see WebAppOrderView) — the panel moves them through the status
    flow and fixes up delivery details, nothing more. No delete either: a
    cancelled order is a record, an absent one is a hole in the books.
    """

    queryset = Order.objects.select_related("user").prefetch_related("items")
    serializer_class = OrderSerializer
    permission_classes = [ModelPermissions]
    pagination_class = DefaultPagination
    filterset_fields = ["status", "delivery_method"]
    search_fields = ["customer_name", "phone_number", "address"]
    ordering_fields = ["created_at", "total"]
    ordering = ["-created_at"]
