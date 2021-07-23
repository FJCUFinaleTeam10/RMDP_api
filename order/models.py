from mongoengine import *
from restaurant.models import restaurant
from driver.models import driver


class order(Document):
    timeRequest = DateTimeField(null=True)
    loadToDriver = BooleanField()

    longitude = StringField(max_length=100)
    latitude = StringField(max_length=100)

    deadlineTime = DateTimeField()
    restaurantId = ReferenceField('restaurant')
    arriveTime = DateTimeField()
    driverId = ReferenceField('driver')

    class Meta:
        db_table = 'order'

# Create your models here.
