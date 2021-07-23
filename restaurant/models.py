from mongoengine import *


# Create your models here.
class restaurant(Document):
    longitude = StringField(max_length=100)
    latitude = StringField(max_length=100)
