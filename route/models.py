from mongoengine import *


class route(Document):
    Driver_ID = StringField()
    Latitude = IntField()
    Longitude = FloatField()
    Node_ID = IntField()
    Order_ID = IntField()
    Restaurant_ID = IntField()
    delivered = IntField()
    nodetype =IntField()