from __future__ import annotations

from asgiref.sync import sync_to_async

from apps.analytics.models import SkinQuizResult
from apps.analytics.skin_logic import QuizResult
from apps.users.models import TelegramUser


@sync_to_async
def save_result(
    *, telegram_id: int, result: QuizResult, language: str
) -> tuple[SkinQuizResult | None, int]:
    """
    Store a finished quiz and adopt its verdict as the customer's skin type.

    Returns the row and the points awarded. Returns (None, 0) for somebody we
    have no card for — the quiz is still worth showing them, it just has
    nowhere to be saved.
    """
    from apps.loyalty.models import PointsTransaction
    from apps.loyalty.services import award

    user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
    if user is None:
        return None, 0

    row = SkinQuizResult.objects.create(
        user=user,
        skin_type=result.skin_type,
        answers=result.answers,
        recommendation_keys=list(result.recommendation_keys),
        language=language,
    )
    TelegramUser.objects.filter(pk=user.pk).update(face_condition=result.skin_type)

    # Only the first run pays: retaking the quiz is welcome, farming it is not.
    outcome = award(
        user,
        PointsTransaction.Reason.QUIZ,
        reference=f"quiz:{user.pk}",
        notify=False,  # the result message says it, one message is enough
    )
    return row, outcome.points
