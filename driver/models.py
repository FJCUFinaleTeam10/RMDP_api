from mongoengine import *


# Create your models here.
class driver(Document):

    Velocity = IntField()
    Capacity = IntField()
    Route = ListField()
    Latitude = FloatField()
    Longitude = FloatField()
    City = StringField()
    Country_Code = IntField()
