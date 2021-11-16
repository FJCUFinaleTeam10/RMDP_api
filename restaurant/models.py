from mongoengine import *


# Create your models here.
class restaurant(Document):
    Address = StringField()
    City_id = IntField()
    Country_Code = IntField(null=True, blank=True)
    Has_Online_delivery = StringField(null=True, blank=True)
    Latitude = StringField(null=True, blank=True)
    Locality = StringField()
    Longitude = StringField(null=True, blank=True)
    Price_range = IntField(null=True, blank=True)
    Restaurant_Name = StringField()
    Votes = IntField(null=True, blank=True)
    order_num = IntField()
    Restaurant_ID = IntField(null=True, blank=True)
    City = StringField(null=True, blank=True)
    Locality_Verbose = StringField()
    Cuisines = StringField(null=True, blank=True)
    Average_Cost_for_two = IntField(null=True, blank=True)
    Currency = StringField(null=True, blank=True)
    Has_Table_booking = StringField(null=True, blank=True)
    Is_delivering_now = StringField(null=True, blank=True)
    Aggregate_rating = FloatField(null=True, blank=True)
    Rating_color = StringField(null=True, blank=True)
    Rating_text = StringField(null=True, blank=True)


