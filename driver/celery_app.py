import os
from datetime import timedelta

from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings')

app = Celery('driver',broker=os.environ.get('DOCKER_CELERY_BROKER_0'))
app.conf.beat_schedule = {
    "driverSimulator": {
        "task": "driver.tasks.updateDriver",
        "schedule": timedelta(seconds=1),
    },
}
app.autodiscover_tasks()
