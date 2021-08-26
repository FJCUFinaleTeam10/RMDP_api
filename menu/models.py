from mongoengine import *


class menu(Document):
    dsc = StringField()
    price = FloatField()
    rate = IntField()
    img = StringField(null=True, blank=True)
    sections = StringField()
    name = StringField()
