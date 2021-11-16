
from mongoengine import *


class all_cities(Document):
    City = StringField()
    City_id = IntField()
    Country_Code = IntField()
    Latitude = FloatField()
    Longitude = FloatField()
    radius = FloatField()


class country_code(Document):
    country = StringField()
    country_code = IntField()