from mongoengine import *


# Create your models here.
class driver(Document):


class test_driver(Document):
    City = StringField()
    Country_Code = IntField()
    Latitude = FloatField()
    Longitude = FloatField()
    Velocity = IntField()
    Capacity = IntField()
    Route = ListField()
