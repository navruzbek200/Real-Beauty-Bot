"""
Public, read-only catalogue for the Telegram Mini App.

The Mini App is a shopfront — the same product names, prices and photos a
customer already sees inside the bot — so it is deliberately unauthenticated
and read-only. Nothing here exposes anything a customer couldn't see by tapping
«Mahsulotlar» in the chat. Writes still go through the authenticated admin API.
"""

from __future__ import annotations

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import Product
from core.i18n import pick

_LANGS = {"uz", "ru", "en"}


def _serialize(product: Product, lang: str, request) -> dict:
    photo = None
    if product.photo and product.photo.name:
        photo = request.build_absolute_uri(product.photo.url)
    return {
        "id": product.pk,
        "name": pick(product, "name", lang),
        "description": pick(product, "description", lang),
        "price": product.current_price or None,
        "old_price": product.old_price or None,
        "discount_percent": product.discount_percent,
        "photo": photo,
        "is_top": product.is_top,
        "top_note": pick(product, "top_note", lang) if product.is_top else "",
    }


class WebAppCatalogView(APIView):
    permission_classes = [AllowAny]
    authentication_classes: list = []

    def get(self, request):
        lang = request.query_params.get("lang", "uz")
        if lang not in _LANGS:
            lang = "uz"
        products = (
            Product.objects.filter(is_active=True)
            .order_by("-is_top", "top_order", "name")
        )
        items = [_serialize(p, lang, request) for p in products]
        return Response({"products": items, "count": len(items)})
