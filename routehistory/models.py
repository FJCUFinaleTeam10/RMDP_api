
from mongoengine import *


# Create your models here.
class routehistory(Document):
    Appear_time = DateTimeField()
    D_id = IntField()
    Finish_time = DateTimeField()
    Latitude = FloatField()
    Longitude = FloatField()
    Method = IntField()
    Node_ID = IntField()
    nodetype = IntField()

