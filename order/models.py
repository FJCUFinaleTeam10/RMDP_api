from mongoengine import *
from restaurant.models import restaurant
from driver.models import driver


class order(Document):
    timeRequest = DateTimeField(null=False)
    loadToDriver = BooleanField()
    iscompleted = BooleanField()
    longitude = StringField(max_length=100)
    latitude = StringField(max_length=100)

    deadlineTime = DateTimeField()
    restaurantId = StringField(max_length=100)
    arriveTime = DateTimeField(null=True)
    driverId = StringField(max_length=100, null=True)

# Create your models here.
