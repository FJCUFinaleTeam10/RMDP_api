from .celery import app as celery_app
import os
import sys
__all__ = ("celery_app",)
sys.path.append(os.path.dirname(os.path.realpath(__file__)))