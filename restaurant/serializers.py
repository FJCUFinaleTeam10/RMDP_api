from rest_framework import serializers
from restaurant.models import restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = restaurant
        # fields = '__all__'
        fields = ('id', 'longitude', 'latitude')
