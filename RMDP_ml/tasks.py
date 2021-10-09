from __future__ import absolute_import, unicode_literals

from celery import shared_task

from RMDP_ml.core import RMDP
from RMDP_ml.userSimulator import userSimulator
from RMDP_ml.driverSimulator import driverSimulator


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
