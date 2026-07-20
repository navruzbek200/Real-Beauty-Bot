from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from core.views import telegram_file

# Global admin polish: clean dash for empty cells + Uzbek titles.
admin.site.empty_value_display = "—"
admin.site.index_title = "Boshqaruv paneli"
# There is no public site. Django defaults this to "/", which puts a
# "Saytni ko'rish" link in the user menu that just bounces back to the admin.
admin.site.site_url = None

urlpatterns = [
    # The admin panel is the whole UI; root just forwards into it.
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/", admin.site.urls),
    # Staff-only proxy to originals that live on Telegram's servers.
    path("tg-file/<str:file_id>/", telegram_file, name="telegram_file"),
]

if settings.DEBUG:
    # Media only. Static is auto-served by django.contrib.staticfiles' finders
    # under runserver — adding a STATIC_URL route here would shadow that and
    # 404 app assets (e.g. django-unfold) since STATIC_ROOT is unpopulated.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
