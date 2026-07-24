from __future__ import annotations

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView
from rest_framework.routers import DefaultRouter

from apps.api.views.analytics import ProgressPhotoViewSet, SkinQuizResultViewSet, UserFeedbackViewSet
from apps.api.views.auth import LoginView, MeView, RefreshView
from apps.api.views.bot_settings import DiscountViewSet, GlobalSettingsView
from apps.api.views.campaigns import (
    AutoMessageLogViewSet,
    AutoMessageViewSet,
    BroadcastViewSet,
    CampaignLogViewSet,
    MessageTemplateViewSet,
)
from apps.api.views.loyalty import (
    LoyaltyAccountViewSet,
    LoyaltySettingsView,
    PointsTransactionViewSet,
    RewardRedemptionViewSet,
    RewardViewSet,
)
from apps.api.views.products import ProductTutorialStepViewSet, ProductViewSet, TopProductViewSet
from apps.api.views.support import (
    SupportAdminViewSet,
    SupportMessageViewSet,
    SupportSettingsTestConnectionView,
    SupportSettingsView,
    SupportThreadViewSet,
)
from apps.api.views.users import AppUserViewSet, StaffViewSet, TelegramUserViewSet, UserProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("top-products", TopProductViewSet, basename="top-product")
router.register("product-tutorial-steps", ProductTutorialStepViewSet, basename="product-tutorial-step")
router.register("customers", TelegramUserViewSet, basename="customer")
router.register("app-users", AppUserViewSet, basename="app-user")
router.register("user-products", UserProductViewSet, basename="user-product")
router.register("staff", StaffViewSet, basename="staff")
router.register("message-templates", MessageTemplateViewSet, basename="message-template")
router.register("campaign-logs", CampaignLogViewSet, basename="campaign-log")
router.register("auto-messages", AutoMessageViewSet, basename="auto-message")
router.register("auto-message-logs", AutoMessageLogViewSet, basename="auto-message-log")
router.register("broadcasts", BroadcastViewSet, basename="broadcast")
router.register("discounts", DiscountViewSet, basename="discount")
router.register("feedback", UserFeedbackViewSet, basename="feedback")
router.register("skin-quiz-results", SkinQuizResultViewSet, basename="skin-quiz-result")
router.register("progress-photos", ProgressPhotoViewSet, basename="progress-photo")
router.register("support-threads", SupportThreadViewSet, basename="support-thread")
router.register("support-messages", SupportMessageViewSet, basename="support-message")
router.register("support-admins", SupportAdminViewSet, basename="support-admin")
router.register("loyalty-accounts", LoyaltyAccountViewSet, basename="loyalty-account")
router.register("points-transactions", PointsTransactionViewSet, basename="points-transaction")
router.register("rewards", RewardViewSet, basename="reward")
router.register("reward-redemptions", RewardRedemptionViewSet, basename="reward-redemption")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="api_login"),
    path("auth/refresh/", RefreshView.as_view(), name="api_refresh"),
    path("auth/me/", MeView.as_view(), name="api_me"),
    path("settings/global/", GlobalSettingsView.as_view(), name="api_global_settings"),
    path("settings/loyalty/", LoyaltySettingsView.as_view(), name="api_loyalty_settings"),
    path("settings/support/", SupportSettingsView.as_view(), name="api_support_settings"),
    path(
        "settings/support/test-connection/",
        SupportSettingsTestConnectionView.as_view(),
        name="api_support_test_connection",
    ),
    path("schema/", SpectacularAPIView.as_view(), name="api_schema"),
    path("", include(router.urls)),
]
