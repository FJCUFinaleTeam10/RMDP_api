import json
import logging

from bson import json_util
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from mongoengine import MultipleObjectsReturned
from rest_framework.decorators import api_view
from route.models import route
from route.serializers import RouteSerializer
from mongoengine.base import get_document as get_model


# Create your views here.
@api_view(['GET'])
def listAll(request):
    offset = int(request.data['skip'])
    items_per_page = int(request.data['limit'])
    orderList = route.objects.skip(offset).limit(items_per_page)
    result = RouteSerializer(orderList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response


@api_view(['POST'])
def createOrder(request):
    try:
        newOrder = route(order_request_time=request.data['requestTime'])
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
    orderList = route.objects.skip(offset).limit(items_per_page)
    result = RouteSerializer(orderList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response


@api_view(['POST'])
def getOrderBaseOnCity(request):
    try:
        cityID = request.data['params']['cityId']
        restaurant = get_model('restaurant')
        filteredCityList = list(restaurant.objects(City_id=cityID).values_list('Restaurant_ID'))

        orderList = route.objects(order_restaurant_carrier_restaurantId__in=filteredCityList)
        result = RouteSerializer(orderList, many=True)
        response = JsonResponse(result.data, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        logging.ERROR


@api_view(['POST'])
def getCurrentRouteBaseOnDriverID(request):
    try:
        driverID = int(request.data['params'].get('driverID', None))

        driverList = route.objects(Driver_ID=driverID)
        result = RouteSerializer(driverList)
        response = JsonResponse(json.loads(json_util.dumps(result.data)), safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return response
    except IntegrityError as IE:
        raise IE
    except MultipleObjectsReturned as ME:
        raise ME
    except Exception as e:
        raise e