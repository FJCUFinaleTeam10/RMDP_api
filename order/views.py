from datetime import datetime, timedelta

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view

from order.models import order
from order.serializers import OrderSerializer
from .tasks import runRMDP


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
    if request.method == 'POST':
        timeRequest = datetime.strptime(request.data['requestTime'], "%d-%m-%Y %H:%M:%S")
        timeDeadline = timeRequest +timedelta(minutes=40)
        newOrder = order(timeRequest=datetime.strptime(request.data['requestTime'], "%d-%m-%Y %H:%M:%S"))
        newOrder.longitude = request.data['longitude']
        newOrder.latitude = request.data['latitude']
        newOrder.deadlineTime = newOrder.timeRequest + timedelta(minutes=40)
        newOrder.restaurantId = request.data['restaurantId']
        newOrder.arriveTime = None
        newOrder.driverId = None
        request.data['orderId']=order.objects.count()+1
        request.data['deadLineTime']= timeDeadline.strftime("%d-%m-%Y %H:%M:%S")
        try:
            runRMDP.delay(request.data)
            return HttpResponse('ok')
        except ValueError:
            print(ValueError)
            return HttpResponseBadRequest("Bad Request")
