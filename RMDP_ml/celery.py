import os
from datetime import timedelta
from celery import Celery
from RMDP_ml.tasks import run_RMDP

modelCelery = Celery("rmdp_ml", broker=[os.environ.get("CELERY_BROKER_2")])
modelCelery.conf.backend = os.environ.get('CELERY_BROKER_2')
modelCelery.conf.broker_url = os.environ.get('CELERY_BROKER_2')

modelCelery.conf.beat_schedule = {
    "run_RMDP": {
        "task": "RMDP_ml.tasks.run_RMDP",
        "schedule": timedelta(seconds=15),
        # 'options': {'queue': os.environ.get('CELERY_BROKER_0')}
    },
}
modelCelery.autodiscover_tasks()
