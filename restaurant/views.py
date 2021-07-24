from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from restaurant.models import restaurant
from restaurant.serializers import RestaurantSerializer


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
