from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view


from restaurant.serializers import RestaurantSerializer, RestaurantListSerializer
from restaurant.models import restaurant



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


@api_view(['POST'])
def getRestaurantList(request):
    offset = int(request.data['params']['skip'])
    items_per_page = int(request.data['params']['limit'])
    restaurantList = restaurant.objects.skip(offset).limit(items_per_page)
    result = RestaurantListSerializer(restaurantList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response
