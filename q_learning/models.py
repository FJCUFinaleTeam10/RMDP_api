from mongoengine import *


class q_learning(Document):
    City = StringField()
    action_index = IntField()
    capacity = IntField()
    decay_rate = FloatField()
    episode = FloatField()
    max_epislon = FloatField()
    min_epislon = FloatField()
    q_table = ListField()
    side_length = FloatField()
    center = ListField()
    epsilon = FloatField()
    nearBY = IntField()
    state_index = IntField()
    gamma = FloatField()
    learning_rate = FloatField()
