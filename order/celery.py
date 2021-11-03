import os
from datetime import timedelta
from celery import Celery
from driver import  tasks

orderCelery = Celery("order", broker=[os.environ.get("CELERY_BROKER_1")])
orderCelery.conf.backend = os.environ.get('CELERY_BROKER_1')
orderCelery.conf.broker_url = os.environ.get('CELERY_BROKER_1')

orderCelery.conf.beat_schedule = {
    "driverSimulator": {
        "task": "order.tasks.generatingOrder",
        "schedule": timedelta(seconds=1),
    },
}
