import os
from datetime import timedelta

from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings')

app = Celery('rmdp', broker=os.environ.get('DOCKER_CELERY_BROKER_0'))

app.conf.beat_schedule = {
    "run_RMDP": {
        "task": "RMDP_ml.tasks.run_RMDP",
        "schedule": timedelta(seconds=15),
    },
}
app.autodiscover_tasks()
