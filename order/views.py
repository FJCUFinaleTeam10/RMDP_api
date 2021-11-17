import logging

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view
from order.models import order
from order.serializers import OrderSerializer
from mongoengine.base import get_document as get_model


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
def getOrderBaseOnCity(request):
    try:
        cityID = request.data['params']['cityId']
        skip = request.data['params'].get('skip', 0)
        limit = request.data['params'].get('limit', 100000000)
        restaurant = get_model('restaurant')
        filteredCityList = list(restaurant.objects(City_id=cityID).values_list('Restaurant_ID'))

        orderList = order.objects(order_restaurant_carrier_restaurantId__in=filteredCityList).skip(skip).limit(limit)
        result = OrderSerializer(orderList, many=True)
        response = JsonResponse(result.data, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        logging.ERROR