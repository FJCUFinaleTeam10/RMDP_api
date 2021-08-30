from mongoengine import *


class all_cities(Document):
    City = StringField()
    Country_Code = IntField()
    Latitude = FloatField()
    Longitude = FloatField()


class country_code(Document):
    country = StringField()
    country_code = IntField()

