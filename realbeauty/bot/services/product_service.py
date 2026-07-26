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

    Order of preference, so a customer never hits a false "you have no
    products" while real products sit in the catalogue:

    1. their own purchases;
    2. any active product that actually has a lesson (top ones first);
    3. failing that, every active product — its card still opens, and the
       detail says "video coming soon" instead of the whole section vanishing.

    The old version only ever showed *top* products that *also* had a lesson,
    so a shop that added a product without ticking "top" saw nothing at all.
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

    with_lessons = list(
        Product.objects.filter(is_active=True, tutorial_steps__isnull=False)
        .distinct()
        .order_by("-is_top", "top_order", "name")
    )
    if with_lessons:
        return with_lessons

    return list(Product.objects.filter(is_active=True).order_by("name"))


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
