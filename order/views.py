from audioop import reverse

from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from datetime import datetime, timedelta

from docutils.parsers import null
from pymongo.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from order.models import order
from order.serializers import OrderSerializer
from driver.models import driver
from driver.serializers import DriverSerializer


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
        newOrder.longitude = request.data['longitude']
        newOrder.latitude = request.data['latitude']
        newOrder.deadlineTime = newOrder.timeRequest + timedelta(minutes=40)
        newOrder.restaurantId = request.data['restaurantId']
        newOrder.arriveTime = null
        newOrder.driverId = null
        newOrder.iscompleted = False
        try:
            newOrder.save()
            return HttpResponseRedirect(reverse('polls:results'))
        finally:
            pass
        return Response("done", status=status.HTTP_201_CREATED)

# @api_view(['GET'])
# def getOrder(request):
#     if request.method == 'GET':
#         newOrder = order(timeRequest=request.data)
#         newOrder.loadToDriver = False
#         newOrder.longitude = StringField(max_length=100)
#         newOrder.latitude = StringField(max_length=100)
#         newOrder.deadlineTime = DateTimeField()
#         newOrder.restaurantId = ReferenceField('restaurant')
#         newOrder.arriveTime = DateTimeField()
#         newOrder.driverId = ReferenceField('driver')
#         newOrder.save()
