from rest_framework import serializers
from order.models import order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = order
        # fields = '__all__'
        fields = ('id', 'timeRequest', 'loadToDriver',
                  'longitude', 'latitude', 'deadlineTime',
                  'restaurantId', 'arriveTime', 'driverId')
