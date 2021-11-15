import logging

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view
from q_learning.models import q_learning
from q_learning.serializers import Q_learningSerializer
from mongoengine.base import get_document as get_model


# Create your views here.
@api_view(['GET'])
def listAll(request):
    offset = int(request.data['skip'])
    items_per_page = int(request.data['limit'])
    orderList = q_learning.objects.skip(offset).limit(items_per_page)
    result = Q_learningSerializer(orderList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response



@api_view(['POST'])
def getSetting(request):
    offset = int(request.data['skip'])
    items_per_page = int(request.data['limit'])
    orderList = q_learning.objects.skip(offset).limit(items_per_page)
    result = Q_learningSerializer(orderList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response

@api_view(['POST'])
def getSettingBaseOnCity(request):
    try:
        cityName = request.data['params']['city']
        restaurant = get_model('restaurant')
        filteredCityList = list(restaurant.objects(City=cityName).values_list('Restaurant_ID'))

        orderList = q_learning.objects(order_restaurant_carrier_restaurantId__in=filteredCityList)
        result = Q_learningSerializer(orderList, many=True)
        response = JsonResponse(result.data, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        print(e)


def getQlearningBaseOnCity(request):
    return None