from celery import shared_task

from RMDP_ml.userSimulator import userSimulator
from order.celery import orderCelery


@shared_task()
def generatingOrder():
    currentTask = userSimulator()
    currentTask.generateThread()
