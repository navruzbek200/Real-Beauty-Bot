from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure-dev-key")

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # project apps
    "apps.users",
    "apps.products",
    "apps.campaigns",
    "apps.bot_settings",
    "apps.analytics",
    "apps.support",
    "apps.loyalty",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "realbeauty"),
        "USER": os.environ.get("POSTGRES_USER", "realbeauty"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# Ours wins over Django's own uz catalogue, which is only partly translated and
# leaves half the admin in English. Rebuild after editing the .po with:
#     python scripts/compile_messages.py
LOCALE_PATHS = [BASE_DIR / "locale"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cache — backs the short-lived Telegram file URLs served by core.views.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    }
}

# Celery
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://redis:6379/0")
CELERY_TIMEZONE = "Asia/Tashkent"
CELERY_ENABLE_UTC = False

# Media / static
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]

# Bot
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "RealBeautyBot")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

# Shared secret the Flutter app sends in the X-Api-Key header when it posts a
# new phone signup to apps.users.api.register_app_user_view.
APP_API_KEY = os.environ.get("APP_API_KEY", "")

# --- Eskiz.uz SMS gateway (phone-signup OTP) ---
ESKIZ_EMAIL = os.environ.get("ESKIZ_EMAIL", "")
ESKIZ_PASSWORD = os.environ.get("ESKIZ_PASSWORD", "")
# Registered sender nickname. Eskiz's shared test nickname works only for
# their sandbox test number until your own nickname/template is approved.
ESKIZ_SMS_FROM = os.environ.get("ESKIZ_SMS_FROM", "4546")

# --- Firebase Admin (mints custom tokens after OTP is verified, so the app
# keeps using Firebase Auth as its one identity system even though the SMS
# itself no longer goes through Firebase Phone Auth) ---
# Path to the service-account JSON downloaded from Firebase Console →
# Project settings → Service accounts → Generate new private key.
FIREBASE_SERVICE_ACCOUNT_JSON = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "")

# --- django-unfold branding ---
from django.templatetags.static import static  # noqa: E402
from django.urls import reverse_lazy  # noqa: E402


def _superuser(request) -> bool:
    return request.user.is_superuser


UNFOLD = {
    "SITE_TITLE": "Real Beauty CRM",
    "SITE_HEADER": "Real Beauty",
    "SITE_SUBHEADER": "Marketing bot boshqaruvi",
    # Logo image (header) + circular avatar/icon (sidebar & favicon).
    "SITE_ICON": lambda request: static("img/real-beauty-icon.svg"),
    "SITE_LOGO": lambda request: static("img/real-beauty-logo.svg"),
    "SITE_FAVICONS": [
        {"rel": "icon", "href": lambda request: static("img/real-beauty-icon.svg")},
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "DASHBOARD_CALLBACK": "core.dashboard.callback",
    "BORDER_RADIUS": "8px",
    # Custom usability CSS (color-coded actions, bigger targets, readability)
    "STYLES": [
        # ?v bust keeps the browser from serving a stale cached copy.
        lambda request: static("css/admin.css") + "?v=9",
    ],
    # Brand palette (navy → cyan), space-separated RGB per Unfold/Tailwind.
    "COLORS": {
        "primary": {
            "50": "236 244 255",
            "100": "216 231 254",
            "200": "185 210 253",
            "300": "141 180 249",
            "400": "96 138 240",
            "500": "61 96 210",
            "600": "43 66 170",
            "700": "33 49 130",
            "800": "26 37 100",
            "900": "23 33 80",
            "950": "15 22 55",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Asosiy",
                "separator": True,
                "items": [
                    {
                        "title": "Boshqaruv paneli",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": "Xaridorlar",
                        "icon": "group",
                        "link": reverse_lazy("admin:users_telegramuser_changelist"),
                    },
                    {
                        "title": "App foydalanuvchilari",
                        "icon": "phone_android",
                        "link": reverse_lazy("admin:users_appuser_changelist"),
                    },
                    {
                        "title": "Murojaatlar",
                        "icon": "forum",
                        "link": reverse_lazy("admin:support_supportthread_changelist"),
                        "badge": "apps.support.badges.awaiting_reply_count",
                    },
                ],
            },
            {
                "title": "Mahsulotlar",
                "separator": True,
                "items": [
                    {
                        "title": "Mahsulotlar",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:products_product_changelist"),
                    },
                    {
                        "title": "Bu oydagi top",
                        "icon": "local_fire_department",
                        "link": reverse_lazy("admin:products_topproduct_changelist"),
                    },
                ],
            },
            {
                "title": "Marketing",
                "separator": True,
                "items": [
                    {
                        "title": "Avtomatik xabarlar",
                        "icon": "schedule_send",
                        "link": reverse_lazy("admin:campaigns_automessage_changelist"),
                        "permission": _superuser,
                    },
                    {
                        "title": "E'lonlar",
                        "icon": "campaign",
                        "link": reverse_lazy("admin:campaigns_broadcast_changelist"),
                        "permission": _superuser,
                    },
                    {
                        "title": "Xabar shablonlari",
                        "icon": "mail",
                        "link": reverse_lazy(
                            "admin:campaigns_messagetemplate_changelist"
                        ),
                        "permission": _superuser,
                    },
                    {
                        "title": "Chegirmalar",
                        "icon": "sell",
                        "link": reverse_lazy("admin:bot_settings_discount_changelist"),
                        "permission": _superuser,
                    },
                    {
                        "title": "Yuborilgan xabarlar",
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:campaigns_campaignlog_changelist"),
                        "permission": _superuser,
                    },
                    {
                        "title": "Avto xabarlar jurnali",
                        "icon": "history",
                        "link": reverse_lazy(
                            "admin:campaigns_automessagelog_changelist"
                        ),
                        "permission": _superuser,
                    },
                ],
            },
            {
                "title": "Bonus dasturi",
                "separator": True,
                "items": [
                    {
                        "title": "Bonus hisoblari",
                        "icon": "loyalty",
                        "link": reverse_lazy("admin:loyalty_loyaltyaccount_changelist"),
                        "permission": _superuser,
                    },
                    {
                        "title": "Sovg'alar",
                        "icon": "redeem",
                        "link": reverse_lazy("admin:loyalty_reward_changelist"),
                        "permission": _superuser,
                    },
                    {
                        "title": "Almashtirilgan sovg'alar",
                        "icon": "confirmation_number",
                        "link": reverse_lazy(
                            "admin:loyalty_rewardredemption_changelist"
                        ),
                    },
                    {
                        "title": "Ball harakatlari",
                        "icon": "swap_vert",
                        "link": reverse_lazy(
                            "admin:loyalty_pointstransaction_changelist"
                        ),
                        "permission": _superuser,
                    },
                    {
                        "title": "Bonus sozlamalari",
                        "icon": "tune",
                        "link": reverse_lazy(
                            "admin:loyalty_loyaltysettings_changelist"
                        ),
                        "permission": _superuser,
                    },
                ],
            },
            {
                "title": "Analitika",
                "separator": True,
                "items": [
                    {
                        "title": "Fikrlar",
                        "icon": "reviews",
                        "link": reverse_lazy("admin:analytics_userfeedback_changelist"),
                    },
                    {
                        "title": "Teri testi natijalari",
                        "icon": "science",
                        "link": reverse_lazy(
                            "admin:analytics_skinquizresult_changelist"
                        ),
                    },
                    {
                        "title": "Natija rasmlari",
                        "icon": "photo_library",
                        "link": reverse_lazy(
                            "admin:analytics_progressphoto_changelist"
                        ),
                    },
                ],
            },
            {
                "title": "Sozlamalar",
                "separator": True,
                "items": [
                    {
                        "title": "Umumiy sozlamalar",
                        "icon": "settings",
                        "link": reverse_lazy(
                            "admin:bot_settings_globalsettings_changelist"
                        ),
                        "permission": _superuser,
                    },
                    {
                        "title": "Xodimlar",
                        "icon": "badge",
                        "link": reverse_lazy("admin:users_staff_changelist"),
                        "permission": _superuser,
                    },
                    {
                        "title": "Telegram guruh",
                        "icon": "forum",
                        "link": reverse_lazy(
                            "admin:support_supportsettings_changelist"
                        ),
                        "permission": _superuser,
                    },
                    {
                        "title": "Guruh adminlari",
                        "icon": "admin_panel_settings",
                        "link": reverse_lazy("admin:support_supportadmin_changelist"),
                        "permission": _superuser,
                    },
                ],
            },
        ],
    },
}
