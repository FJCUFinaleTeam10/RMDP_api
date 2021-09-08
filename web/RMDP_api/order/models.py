from mongoengine import *


class order(Document):
    order_approved_at = StringField()
    order_customer_Latitude = FloatField()
    order_customer_Longitude = FloatField()

    order_delivered_customer_date = StringField()
    order_estimated_delivery_date = StringField()

    order_request_time = StringField()
    order_restaurant_carrier_date = StringField()
    order_restaurant_carrier_restaurantId = IntField()
    order_status = StringField()
# Create your models here.
