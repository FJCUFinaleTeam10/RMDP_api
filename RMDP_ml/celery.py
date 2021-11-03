import os
from datetime import timedelta
from celery import Celery
from RMDP_ml.tasks import run_RMDP

driverCelery = Celery("driver", broker=[os.environ.get("CELERY_BROKER_2")])
driverCelery.conf.backend = os.environ.get('CELERY_BROKER_2')
driverCelery.conf.broker_url = os.environ.get('CELERY_BROKER_2')

driverCelery.conf.beat_schedule = {
    "driverSimulator": {
        "task": "RMDP_ml.tasks.run_RMDP",
        "schedule": timedelta(seconds=1),
    },
}
