
from mongoengine import *


# Create your models here.
class driver(Document):
    Capacity = IntField()
    City = StringField()
    Country_Code = IntField()
    Driver_ID = StringField()
    Latitude = FloatField()
    Longitude = FloatField()
    Reward = FloatField()
    Velocity = IntField()
    Route = ListField()
    Route = ListField()
    State = IntField()