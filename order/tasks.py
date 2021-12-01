from celery import shared_task

from RMDP_ml import userSimulator


@shared_task
def generatingOrder():
    userSimulator.generateThread()

