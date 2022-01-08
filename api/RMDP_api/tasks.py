'''from celery import shared_task
from celery.utils.log import get_task_logger

from RMDP_ml.core import RMDP
from RMDP_ml.userSimulator import userSimulator
from RMDP_ml.driverSimulator import driverSimulator
from RMDP_ml.new_core import SA
currentAssign = SA()
currentGenerate = userSimulator()
currentUpdate = driverSimulator()

generateDataTime = 4
for time_tik in range(0,10800+1):
    if time_tik%generateDataTime == 0:
        currentGenerate.generateThread()'''
