import os
from celery import Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
app = Celery("core", broker=[os.environ.get("CELERY_BROKER")])
# Using a string here means the worker doesn't have to serialize
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
