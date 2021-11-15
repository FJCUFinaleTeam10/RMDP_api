from mongoengine import *


class q_learning(Document):
    City_id = IntField()
    action_index = IntField()
    center = ListField()
    decay_rate = FloatField()
    episode = FloatField()
    max_epislon = FloatField()
    min_epislon = FloatField()
    q_table = ListField()
    side_length = FloatField()
    capacity = IntField()
    epsilon = FloatField()
    nearBY = IntField()
    state_index = IntField()
    gamma = FloatField()
    learning_rate = FloatField()
