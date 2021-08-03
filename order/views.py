from datetime import datetime, timedelta
from datetime import datetime, timedelta

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view

from order.models import order
from order.serializers import OrderSerializer
from .tasks import send_email


# Create your views here.
@api_view(['GET', 'POST', 'DELETE'])
def listAll(request):
    if request.method == 'GET':
        result = OrderSerializer(order.objects.all(), many=True)
        response = JsonResponse(result.data, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return response


@api_view(['POST'])
def createOrder(request):
    if request.method == 'POST':

        newOrder = order(timeRequest=datetime.strptime(request.data['requestTime'], "%d-%m-%Y %H:%M:%S"))
        newOrder.loadToDriver = False
        newOrder.iscompleted = False
        newOrder.longitude = request.data['longitude']
        newOrder.latitude = request.data['latitude']
        newOrder.deadlineTime = newOrder.timeRequest + timedelta(minutes=40)
        newOrder.restaurantId = request.data['restaurantId']
        newOrder.arriveTime = None
        newOrder.driverId = None

        newOrder.driverId = None

        try:
            send_email.delay('danghoangnhan.1@gmail.com', 'daniel')
            newOrder.save()
            return HttpResponse('ok')
        except ValueError:
            return  HttpResponseBadRequest("Bad Request")
