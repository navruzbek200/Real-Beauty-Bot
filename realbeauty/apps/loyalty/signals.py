"""
Points are credited where the thing actually happens, not where somebody
remembered to call the service.

A purchase can be entered by staff in the CRM, imported by a script or created
by the bot; hanging the award off `post_save` means all three routes pay out,
and none of them has to know the loyalty program exists.
"""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.analytics.models import ProgressPhoto, UserFeedback
from apps.loyalty.models import PointsTransaction
from apps.loyalty.services import award
from apps.users.models import UserProduct


@receiver(post_save, sender=UserProduct, dispatch_uid="loyalty_purchase")
def credit_purchase(sender, instance: UserProduct, created: bool, **kwargs) -> None:
    if not created:
        return
    award(
        instance.user,
        PointsTransaction.Reason.PURCHASE,
        reference=f"userproduct:{instance.pk}",
        note=instance.product.name[:200],
    )


@receiver(post_save, sender=UserFeedback, dispatch_uid="loyalty_feedback")
def credit_feedback(sender, instance: UserFeedback, created: bool, **kwargs) -> None:
    if not created:
        return
    award(
        instance.user,
        PointsTransaction.Reason.FEEDBACK,
        reference=f"feedback:{instance.pk}",
    )


@receiver(post_save, sender=ProgressPhoto, dispatch_uid="loyalty_progress")
def credit_progress(sender, instance: ProgressPhoto, created: bool, **kwargs) -> None:
    # A before/after pair is one submission, and the "after" shot is the half
    # that shows a result — paying per photo would double the reward for
    # sending the same thing twice.
    if not created or instance.label != ProgressPhoto.Label.AFTER:
        return
    award(
        instance.user,
        PointsTransaction.Reason.PROGRESS,
        reference=f"progress:{instance.pk}",
    )
