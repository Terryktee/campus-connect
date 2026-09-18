import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campusloop.settings")

app = Celery("campusloop")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
