from mongoengine import *


class route(Document):
    delivered = IntField()
    Driver_ID = IntField()
    Latitude = FloatField()
    Longitude = FloatField()
    Node_ID = IntField()
    nodetype = IntField()
    Order_ID = IntField()
    Restaurant_ID = FloatField()

