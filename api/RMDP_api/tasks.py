from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command
from .RMDP_ml.core import RMDP
from .RMDP_ml.userSimulator import userSimulator
# from .RMDP_ml.driverSimulator import driverSimulator
logger = get_task_logger(__name__)

@shared_task
def sample_task():
    logger.info("The sample task just ran.")

@shared_task
def send_email_report():
    call_command("email_report", )

@shared_task
def run_RMDP():
    currentTask = RMDP()
    currentTask.generateThread()

@shared_task
def generatingOrder():
    currentTask = userSimulator()
    currentTask.generateThread()

# @shared_task
# def updateDriver():
#     currentTask = driverSimulator()
#     currentTask.generateThread()
