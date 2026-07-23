from __future__ import annotations

from asgiref.sync import sync_to_async

from apps.products.models import Product, ProductTutorialStep


@sync_to_async
def get_active_products() -> list[Product]:
    return list(Product.objects.filter(is_active=True))


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
