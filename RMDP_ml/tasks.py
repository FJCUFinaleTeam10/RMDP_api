from __future__ import absolute_import, unicode_literals

from celery import shared_task

from RMDP_ml import core
from RMDP_ml import userSimulator
from RMDP_ml import driverSimulator


@shared_task
def run_RMDP():
    core.generateThread()


@shared_task
def generatingOrder():
    userSimulator.generateThread()


@shared_task
def updateDriver():
    driverSimulator.generateThread()
