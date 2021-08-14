from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer

from restaurants.models import test_restaurant


class RestaurantsSerializer(DocumentSerializer):
    class Meta:
        model = test_restaurant
        fields = '__all__'