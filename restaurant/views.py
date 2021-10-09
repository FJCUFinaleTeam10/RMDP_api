from django.http import JsonResponse
from rest_framework.decorators import api_view

from .models import restaurant
from .serializers import RestaurantSerializer


@api_view(['POST'])
def listAllRestaurantList(request):
    restaurantList = restaurant.objects.all()
    result = RestaurantSerializer(restaurantList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


@api_view(['POST'])
def getRestaurantBaseOnCity(request):
    cityName = request.data['params']['city']
    restaurantList = restaurant.objects(City=cityName)
    result = RestaurantSerializer(restaurantList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


@api_view(['POST'])
def getRestaurantBaseOnId(request):
    restId = int(request.data['params']['restId'])
    restaurantList = restaurant.objects(Restaurant_ID=restId)
    result = RestaurantSerializer(restaurantList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


@api_view(['POST'])
def listRestaurantList(request):
    skip = request.data['params']['skip']
    limit = request.data['params']['limit']
    restaurantList = []

    if 'city' in request.data['params']:
        cityName = request.data['params']['city']
        restaurantList = restaurant.objects(City=cityName).skip(skip).limit(limit)
    else:
        restaurantList = restaurant.objects.skip(skip).limit(limit)
    result = RestaurantSerializer(restaurantList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response
