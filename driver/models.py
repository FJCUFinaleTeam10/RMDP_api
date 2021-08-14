from mongoengine import *


# Create your models here.
class driver(Document):
    longitude = StringField(max_length=100)
    latitude = StringField(max_length=100)
    velocity = FloatField()
    capacity = FloatField()
    route = ListField()

class Generate_Driver(Document):
    longitude = StringField(max_length=100)
    latitude = StringField(max_length=100)
    velocity = FloatField()
    capacity = FloatField()
    route = ListField()
