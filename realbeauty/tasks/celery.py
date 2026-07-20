from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.prod")

app = Celery("realbeauty", include=["tasks.scheduled", "tasks.broadcast"])
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "week1-checkin": {
        "task": "tasks.scheduled.send_week1_checkins",
        "schedule": crontab(hour=10, minute=0),  # 10:00 Tashkent
    },
    "week2-progress": {
        "task": "tasks.scheduled.send_week2_progress",
        "schedule": crontab(hour=10, minute=30),
    },
    "birthday-messages": {
        "task": "tasks.scheduled.send_birthday_messages",
        "schedule": crontab(hour=9, minute=0),
    },
    # Housekeeping — keeps the log table and media dir from growing forever.
    "purge-campaign-logs": {
        "task": "tasks.scheduled.purge_old_campaign_logs",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),
    },
    "purge-progress-thumbnails": {
        "task": "tasks.scheduled.purge_old_progress_thumbnails",
        "schedule": crontab(hour=3, minute=30, day_of_week=0),
    },
    "purge-admin-log": {
        "task": "tasks.scheduled.purge_old_admin_log",
        "schedule": crontab(hour=3, minute=45, day_of_week=0),
    },
}
