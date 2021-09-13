from mongoengine import *


class order(Document):
    order_approved_at = StringField()
    driver_id = StringField()
    Latitude = FloatField()
    Longitude = FloatField()

    order_delivered_customer_date = StringField()
    order_estimated_delivery_date = StringField()

    order_request_time = StringField()
    order_restaurant_carrier_date = StringField()
    order_restaurant_carrier_restaurantId = IntField()
    order_status = StringField()
    Order_ID = StringField()
    customer_phone_number = StringField()
# Create your models here.
