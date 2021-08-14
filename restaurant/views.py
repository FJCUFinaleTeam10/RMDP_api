from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from restaurant.models import restaurant
from restaurant.serializers import RestaurantSerializer
from restaurants.models import test_restaurant
from restaurants.serializer import RestaurantsSerializer


@api_view(['GET', 'POST', 'DELETE'])
def listAll(request):
    if request.method == 'GET':
        restaurantList = restaurant.objects.all()
        result = RestaurantSerializer(restaurantList, many=True)
        response = JsonResponse(result.data, safe=False)
        return response
    if request.method == 'POST':
        pass
    if request.method == 'DELETE':
        pass


@api_view(['GET'])
def getRestaurantList(request):
    offset = int(request.data['skip'])
    items_per_page = int(request.data['limit'])
    restaurantList = test_restaurant.objects.skip(offset).limit(items_per_page)
    result = RestaurantsSerializer(restaurantList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response
