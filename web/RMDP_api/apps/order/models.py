from mongoengine import *


class order(Document):
    order_approved_at = StringField()
    order_customer_Latitude = IntField()
    order_customer_Longitude = IntField()

    order_delivered_customer_date = StringField()
    order_estimated_delivery_date = StringField()

    order_request_time = StringField()
    order_restaurant_carrier_date = StringField()
    order_status = StringField()
# Create your models here.
