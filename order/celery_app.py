import os
from datetime import timedelta

from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings')

app = Celery('order', broker=os.environ.get('DOCKER_CELERY_BROKER_0'))
app.conf.beat_schedule = {
    "generatingOrder": {
        "task": "order.tasks.generatingOrder",
        "schedule": timedelta(seconds=15),
    },
}
app.autodiscover_tasks()
