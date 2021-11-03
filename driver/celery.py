import os
from datetime import timedelta
from celery import Celery
from driver.tasks import driverSimulator

driverCelery = Celery("driver", broker=[os.environ.get("CELERY_BROKER_0")])
driverCelery.conf.backend = os.environ.get('CELERY_BROKER_0')
driverCelery.conf.broker_url = os.environ.get('CELERY_BROKER_0')

driverCelery.conf.beat_schedule = {
    "driverSimulator": {
        "task": "driver.tasks.updateDriver",
        "schedule": timedelta(seconds=1),
    },
}
