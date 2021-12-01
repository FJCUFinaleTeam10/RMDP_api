
from mongoengine import *


# Create your models here.
class driver(Document):
    Capacity = IntField()
    City_id = IntField()
    Driver_ID = IntField()
    Latitude = FloatField()
    Longitude = FloatField()
    Node_ID = IntField()
    Reward = FloatField()
    Node_num = IntField()
    Velocity = IntField()
    City = StringField()
    State = IntField()

