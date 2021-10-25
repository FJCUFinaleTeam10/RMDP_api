from mongoengine import *


# Create your models here.
class RMDP_env(Document):
    Order_num = IntField()
    all_driver_routing_Theta_x = ListField()
    capacity = IntField()
    deadlineTime = IntField()
    delay = IntField()
    maxLengthPost = IntField()
    maxtime_of_system_



