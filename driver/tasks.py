from celery import shared_task
from RMDP_ml.driverSimulator import driverSimulator


@shared_task
def generatingOrder():
    currentTask = driverSimulator()
    currentTask.generateThread()
