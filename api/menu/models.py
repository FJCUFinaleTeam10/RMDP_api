from mongoengine import *


class menu(Document):
    dsc = StringField()
    price = FloatField()
    rate = IntField()
    img = StringField(null=True, blank=True)
    section = StringField()
    name = StringField()
    menu = ListField()
    restaurant_id = IntField()