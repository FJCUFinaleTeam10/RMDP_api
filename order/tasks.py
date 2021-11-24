from celery import shared_task

from RMDP_ml import new_core
from RMDP_ml import userSimulator
from RMDP_ml import driverSimulator


@shared_task
def generatingOrder():
    userSimulator.generateThread()

