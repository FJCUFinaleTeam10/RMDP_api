
from mongoengine import *


# Create your models here.
class driver(Document):
    Capacity = IntField()
    Country_Code = IntField()
    Driver_ID = StringField()
    Latitude = FloatField()
    Longitude = FloatField()
    Reward = FloatField()
    Velocity = FloatField()
    City = StringField()
    State = IntField()
    Route = ListField()
