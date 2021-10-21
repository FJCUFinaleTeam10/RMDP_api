from celery import shared_task

from RMDP_ml.userSimulator import userSimulator
from RMDP_ml.driverSimulator import driverSimulator
from RMDP_ml.new_core import SA


@shared_task
def run_RMDP():
    currentTask = SA()
    currentTask.generateThread()


@shared_task
def generatingOrder():
    currentTask = userSimulator()
    currentTask.generateThread()


@shared_task
def updateDriver():
    currentTask = driverSimulator()
    currentTask.generateThread()
