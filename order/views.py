import json
import logging

from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from mongoengine import MultipleObjectsReturned
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser

from order.models import order
from order.serializers import OrderSerializer
from mongoengine.base import get_document as get_model
from bson import json_util

# Create your views here.
@api_view(['GET'])
def listAll(request):
    offset = int(request.data['skip'])
    items_per_page = int(request.data['limit'])
    orderList = order.objects.skip(offset).limit(items_per_page)
    result = OrderSerializer(orderList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response


@api_view(['POST'])
def createOrder(request):
    try:
        newOrder = order(order_request_time=request.data['requestTime'])
        newOrder.order_restaurant_carrier_restaurantId = int(request.data['restaurantId'])
        newOrder.order_delivered_customer_date = None
        newOrder.driverId = None
        newOrder.order_approved_at = ""
        newOrder.order_restaurant_carrier_date = None
        newOrder.order_status = 'unassign'
        newOrder.order_customer_Longitude = float(request.data['longitude'])
        newOrder.order_customer_Latitude = float(request.data['latitude'])
        newOrder.save()
        return HttpResponse('ok')
    except ValueError:
        print(ValueError)
        return HttpResponseBadRequest(ValueError)


@api_view(['POST'])
def getOrder(request):
    offset = int(request.data['skip'])
    items_per_page = int(request.data['limit'])
    orderList = order.objects.skip(offset).limit(items_per_page)
    result = OrderSerializer(orderList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response


@api_view(['POST'])
@parser_classes([JSONParser])
def getOrderBaseOnCity(request):
    try:
        cityID = request.data['params'].get('cityId', 'Agra')
        skip = request.data['params'].get('skip', 0)
        limit = request.data['params'].get('limit', 100000000)
        restaurant = get_model('restaurant')
        filteredCityList = list(restaurant.objects(City_id=cityID).values_list('Restaurant_ID'))
        orderList = order.objects(order_restaurant_carrier_restaurantId__in=filteredCityList).skip(skip).limit(limit)
        totalValue = order.objects(order_restaurant_carrier_restaurantId__in=filteredCityList).count()
        result = OrderSerializer(orderList, many=True)
        response = {}
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        response['count'] = totalValue
        response['data'] = json.loads(json_util.dumps(result.data))
        return JsonResponse(response)
    except IntegrityError as IE:
        print(IE)
    except MultipleObjectsReturned as ME:
        print(ME)
    except Exception as e:
        print(e)