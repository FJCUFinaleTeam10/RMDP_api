from mongoengine import *


# Create your models here.
class driver(Document):
    Capacity = IntField()
    City = StringField()
    Country_Code = IntField()
    Latitude = FloatField()
    Longitude = FloatField()
    Route = ListField()
    Velocity = IntField()


