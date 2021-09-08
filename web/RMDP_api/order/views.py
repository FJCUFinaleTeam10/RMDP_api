from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view
from .models import order
from .serializers import OrderSerializer
from django.apps import apps
from..restaurant.models import restaurant
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
        newOrder = order(order_request_time=datetime.strptime(request.data['requestTime'], "%d-%m-%Y %H:%M:%S"))
        newOrder.order_restaurant_carrier_restaurantId = request.data['restaurantId']
        newOrder.order_delivered_customer_date = None
        newOrder.driverId = None
        newOrder.order_approved_at = None
        newOrder.deliveried_customed_date = None
        newOrder.order_restaurant_carrier_date = None
        newOrder.order_status = 'unassign'
        newOrder.delivered_customer_Longitude = request.data['params']['longitude']
        newOrder.delivered_customer_Latitude = request.data['params']['latitude']
        newOrder.orderId = order.objects.count() + 1
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
    cityName = request.data['params']['city']
    filteredCityList = restaurant.objects(City=cityName).values_list('id')
    orderList = order.objects(cityName in filteredCityList)
    result = OrderSerializer(orderList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response