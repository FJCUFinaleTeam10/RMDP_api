

from mongoengine import *


# Create your models here.
class RMDP_env(Document):
    capacity = IntField()
    deadlineTime = IntField()
    delay = IntField()
    maxLengthPost = IntField()
    restaurantPrepareTime = IntField()
    t_Pmax = IntField()
    t_ba = IntField()
    time_buffer = IntField()
    velocity = FloatField()
