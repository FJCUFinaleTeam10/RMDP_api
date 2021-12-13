from mongoengine import *


class history(Document):
    D_id = IntField()
    Latitude = FloatField()
    Longitude = FloatField()
    Method = IntField()
    Time = DateTimeField()