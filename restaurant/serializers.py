from rest_framework_mongoengine.serializers import DocumentSerializer

from restaurant.models import restaurant


class RestaurantSerializer(DocumentSerializer):
    class Meta:
        model = restaurant
        fields = '__all__'
