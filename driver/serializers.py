from rest_framework import serializers
from driver.models import driver


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = driver
        # fields = '__all__'
        fields = ('id', 'longitude', 'latitude',
                  'velocity', 'capacity')
