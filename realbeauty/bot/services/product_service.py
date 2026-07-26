from __future__ import annotations

from asgiref.sync import sync_to_async

from apps.products.models import Product, ProductTutorialStep


@sync_to_async
def get_active_products() -> list[Product]:
    return list(Product.objects.filter(is_active=True))


@sync_to_async
def get_active_products_page(offset: int, limit: int) -> tuple[list[Product], int]:
    """One page of the catalogue plus the full count, in a single round trip.

    LIMIT/OFFSET at the database keeps the catalogue answer cheap no matter how
    many products the shop ends up with — the whole point of paginating instead
    of shipping one card per product.
    """
    qs = Product.objects.filter(is_active=True).order_by("name")
    total = qs.count()
    return list(qs[offset : offset + limit]), total


@sync_to_async
def get_top_products() -> list[Product]:
    """
    This month's curated top list.

    Deactivated products are filtered out even when still flagged as top: the
    shop switches a product off when it stops selling it, and forgetting to
    untick the top flag must not keep advertising it.
    """
    return list(
        Product.objects.filter(is_top=True, is_active=True).order_by(
            "top_order", "name"
        )
    )


@sync_to_async
def get_product(product_id: int) -> Product | None:
    return Product.objects.filter(pk=product_id).first()


@sync_to_async
def get_tutorial_products(telegram_id: int) -> list[Product]:
    """Products whose lessons a customer can open from «Tarkiblar».

    Their own purchases first. A brand-new customer with nothing on file
    shouldn't hit a dead end, so we fall back to this month's top products that
    actually have a lesson attached — a promo card with no steps behind it would
    just confuse in a "learn the ingredients" context.
    """
    owned = list(
        Product.objects.filter(
            userproduct__user__telegram_id=telegram_id, is_active=True
        )
        .distinct()
        .order_by("name")
    )
    if owned:
        return owned
    return list(
        Product.objects.filter(
            is_top=True, is_active=True, tutorial_steps__isnull=False
        )
        .distinct()
        .order_by("top_order", "name")
    )


@sync_to_async
def get_tutorial_steps(product_id: int) -> list[ProductTutorialStep]:
    return list(
        ProductTutorialStep.objects.filter(product_id=product_id).order_by("order")
    )


@sync_to_async
def get_tutorial_step(step_id: int) -> ProductTutorialStep | None:
    return (
        ProductTutorialStep.objects.select_related("product")
        .filter(pk=step_id)
        .first()
    )


@sync_to_async
def cache_video_file_id(step_id: int, file_id: str) -> None:
    """Persist the Telegram file_id after the first upload send (reuse later)."""
    ProductTutorialStep.objects.filter(pk=step_id).update(video_file_id=file_id)
