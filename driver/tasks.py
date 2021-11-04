from celery import shared_task
from RMDP_ml.driverSimulator import driverSimulator


@shared_task
def updateDriver():
    currentTask = driverSimulator()
    currentTask.generateThread()
