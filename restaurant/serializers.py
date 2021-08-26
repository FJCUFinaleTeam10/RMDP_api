from rest_framework_mongoengine.serializers import DocumentSerializer

from restaurant.models import restaurant,test_restaurant


class RestaurantSerializer(DocumentSerializer):
    class Meta:
        model = restaurant
        fields = '__all__'

class testRestaurantsSerializer(DocumentSerializer):
    class Meta:
        model = test_restaurant
        fields = '__all__'
