from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer

from restaurants.models import resteraurants
class RestaurantsSerializer(DocumentSerializer):
    class Meta:
        model = resteraurants
        fields = '__all__'
        # fields = ('id', 'longitude', 'latitude')