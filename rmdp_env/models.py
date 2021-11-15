from mongoengine import *


class rmdp_env(Document):
    capacity = IntField()
    deadlineTime = IntField()
    delay = IntField()
    maxLengthPost = IntField()
    restaurantPrepareTime = IntField()
    t_Pmax = IntField()
    t_ba = StringField()
    time_buffer = IntField()
    velocity = FloatField()
