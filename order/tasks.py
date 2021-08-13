from __future__ import absolute_import, unicode_literals

from celery import task
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

from RMDP.RMDP import RMDP
from celery.contrib import  rdb

@task
def send_email(recipient_email, recipient_name):
    try:
        subject = 'Test sending email'
        message = 'hello {}'.format(recipient_name)
        mail_sent = send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # 寄件人的信箱
            [recipient_email]  # 收件人的信箱
        )
        print(mail_sent)
        return mail_sent
    except ValueError:
        print(ValueError)


@task
def runRMDP(unAsignerOrder):
    print(unAsignerOrder)
    delay = float('inf')
    maxLengthPost: int = 10  # p_max
    maxTimePost: int = 20  # minutes     #t_pmax
    capacity: int = 10
    velocity: int = 20
    restaurantRepareTime: int = 10 * 60
    deadlineTime :int = 40
    instance = RMDP(delay, maxLengthPost, maxTimePost, capacity, velocity, restaurantRepareTime,deadlineTime)
    currentTime = now()
    instance.runRMDP([unAsignerOrder])
