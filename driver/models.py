
from mongoengine import *


# Create your models here.
class driver(Document):
    Capacity = IntField()
    City_id = IntField()
    Country_Code = IntField()
    Driver_ID = StringField()
    Latitude = FloatField()
    Longitude = FloatField()
    Node_ID = IntField()
    Node_num = IntField()
    Reward = FloatField()
    State = IntField()
    Velocity = IntField()
