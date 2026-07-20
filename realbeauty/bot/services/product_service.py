from __future__ import annotations

from asgiref.sync import sync_to_async

from apps.products.models import Product, ProductTutorialStep


@sync_to_async
def get_active_products() -> list[Product]:
    return list(Product.objects.filter(is_active=True))


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
