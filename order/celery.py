import os
from datetime import timedelta
from celery import Celery
from order.task import generatingOrder

orderCelery = Celery("order", broker=[os.environ.get("CELERY_BROKER_1")])
orderCelery.conf.backend = os.environ.get('CELERY_BROKER_1')
orderCelery.conf.broker_url = os.environ.get('CELERY_BROKER_1')

orderCelery.conf.beat_schedule = {
    "generatingOrder": {
        "task": "order.task.generatingOrder",
        "schedule": timedelta(seconds=15),
        # 'options': {'queue': os.environ.get('CELERY_BROKER_1')}
    },
}

orderCelery.autodiscover_tasks()
