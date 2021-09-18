from celery import shared_task
from celery.utils.log import get_task_logger

from RMDP_ml.core import RMDP
from RMDP_ml.userSimulator import userSimulator
from RMDP_ml.driverSimulator import driverSimulator

er = get_task_logger(__name__)


@shared_task
def run_RMDP():
    currentTask = RMDP()
    currentTask.generateThread()


@shared_task
def generatingOrder():
    currentTask = userSimulator()
    currentTask.generateThread()


@shared_task
def updateDriver():
    currentTask = driverSimulator()
    currentTask.generateThread()
