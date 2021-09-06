from mongoengine import *


class order(Document):
    order_approved_at = StringField()
    order_delivered_customer_date = StringField()
    order_estimated_delivery_date = StringField()
    order_restaurant_carrier_date = StringField()
    order_status = StringField()
# Create your models here.
