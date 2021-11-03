# Celery configuration
# http://docs.celeryproject.org/en/latest/configuration.html
import os
from datetime import timedelta

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_1")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER_1")

# json serializer is more secure than the default pickle
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'

# Use UTC instead of localtime
CELERY_ENABLE_UTC = True

# Maximum retries per task
CELERY_TASK_ANNOTATIONS = {'*': {'max_retries': 3}}

# A custom property used in tasks.py:run()
CUSTOM_RETRY_DELAY = 10
CELERY_BEAT_SCHEDULE = {
    "generatingOrder": {
        "task": "order.tasks.generatingOrder",
        "schedule": timedelta(seconds=15),
        'options': {'queue': os.environ.get('CELERY_BROKER_1')}
    }
}

