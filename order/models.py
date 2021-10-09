from mongoengine import *


class order(Document):
    driver_id = StringField()
    order_approved_at = StringField()

    Latitude = FloatField()
    Longitude = FloatField()
    Order_ID = StringField()
    customer_phone_number = StringField()
    Qtable_position = IntField()
    order_delivered_customer_date = StringField()
    Qtable_updated = IntField()
    order_estimated_delivery_date = StringField()
    order_request_time = StringField()
    order_restaurant_carrier_date = StringField()
    order_restaurant_carrier_restaurantId = IntField()
    order_status = StringField()