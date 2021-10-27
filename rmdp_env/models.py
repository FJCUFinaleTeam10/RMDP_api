

from mongoengine import *


# Create your models here.
class rmdp_env(Document):
    capacity = IntField()
    deadlineTime = IntField()
    delay = IntField()
    maxLengthPost = IntField()
    restaurantPrepareTime = IntField()
    t_Pmax = IntField()
    City = StringField()
    t_ba = IntField()
    time_buffer = IntField()
    velocity = FloatField()
