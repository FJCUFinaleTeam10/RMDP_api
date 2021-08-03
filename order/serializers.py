from rest_framework import serializers
from order.models import order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = order
        fields = '__all__'
