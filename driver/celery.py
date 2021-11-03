import os
from datetime import timedelta

from celery import Celery

driverCelery = Celery("driver", broker=[os.environ.get("CELERY_BROKER_0")])
driverCelery.conf.backend = os.environ.get('CELERY_BROKER_0')
driverCelery.conf.broker_url = os.environ.get('CELERY_BROKER_0')
driverCelery.conf.beat_schedule = {
    "driverSimulator": {
        "task": "RMDP_ml.tasks.run_RMDP",
        "schedule": timedelta(seconds=15),
        # 'options': {'queue': os.environ.get('CELERY_BROKER_0')}
    },
}
driverCelery.autodiscover_tasks()
