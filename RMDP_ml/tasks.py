from celery import shared_task

from RMDP_ml import new_core


@shared_task
def run_RMDP():
    new_core.generateThread()

