from __future__ import annotations

from dataclasses import dataclass

from asgiref.sync import sync_to_async

from apps.loyalty.models import (
    LoyaltyAccount,
    LoyaltySettings,
    PointsTransaction,
    Reward,
    RewardRedemption,
)
from apps.loyalty.services import REASON_LABEL_KEY, TierInfo, redeem, tier_for
from apps.users.models import TelegramUser


@dataclass(frozen=True)
class LoyaltyCard:
    """Everything the "Bonuslarim" screen shows, fetched in one round trip."""

    balance: int
    lifetime: int
    tier: TierInfo
    settings: LoyaltySettings
    has_rewards: bool


@dataclass(frozen=True)
class HistoryEntry:
    points: int
    reason_key: str
    date: str


@sync_to_async
def get_card(telegram_id: int) -> LoyaltyCard | None:
    settings = LoyaltySettings.get()
    if not settings.is_enabled:
        return None
    user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
    if user is None:
        return None
    account, _ = LoyaltyAccount.objects.get_or_create(user=user)
    return LoyaltyCard(
        balance=account.balance,
        lifetime=account.lifetime_points,
        tier=tier_for(account.lifetime_points, settings),
        settings=settings,
        has_rewards=Reward.objects.filter(is_active=True).exists(),
    )


@sync_to_async
def get_history(telegram_id: int, limit: int = 10) -> list[HistoryEntry]:
    rows = PointsTransaction.objects.filter(user__telegram_id=telegram_id)[:limit]
    return [
        HistoryEntry(
            points=row.points,
            reason_key=REASON_LABEL_KEY.get(row.reason, "loyalty.reason.manual"),
            date=row.created_at.strftime("%d.%m.%Y"),
        )
        for row in rows
    ]


@sync_to_async
def get_rewards() -> list[Reward]:
    """Claimable rewards only — a sold-out row on screen is a dead button."""
    return [r for r in Reward.objects.filter(is_active=True) if r.is_available]


@sync_to_async
def redeem_reward(telegram_id: int, reward_id: int) -> tuple[RewardRedemption, int]:
    """Claim a reward; returns the redemption and the remaining balance."""
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    redemption = redeem(user, reward_id)
    balance = LoyaltyAccount.objects.get(user=user).balance
    return redemption, balance


@sync_to_async
def get_summary(telegram_id: int) -> tuple[int, str]:
    """(balance, tier label key) for the profile line."""
    account = (
        LoyaltyAccount.objects.filter(user__telegram_id=telegram_id)
        .select_related("user")
        .first()
    )
    if account is None:
        return 0, "loyalty.tier.bronze"
    return account.balance, tier_for(account.lifetime_points).label_key
