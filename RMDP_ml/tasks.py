from celery import shared_task



from RMDP_ml import new_core
from RMDP_ml import userSimulator
from RMDP_ml import driverSimulator

'''
@shared_task
def run_RMDP():
    new_core.generateThread()
'''

@shared_task
def generatingOrder():
    userSimulator.generateThread()

'''
@shared_task
def updateDriver():
    driverSimulator.generateThread()
'''