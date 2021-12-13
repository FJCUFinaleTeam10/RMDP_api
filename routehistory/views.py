# Create your views here.
import json
from dateutil import parser

from bson import json_util
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from mongoengine import MultipleObjectsReturned
from requests import Response
from rest_framework.decorators import api_view

from driver.models import driver
from routehistory.models import routehistory
from routehistory.serializers import RouteHistorySerializer
from mongoengine.queryset.visitor import Q

# Create your views here.
@api_view(['POST'])
def getHistoryBaseOnDriverID(request):
    cityID = int(request.data['params'].get('cityID', None))
    fromDate = parser.parse(request.data['params'].get('from', None))
    toDate = parser.parse(request.data['params'].get('to', None))
    driverList = list(driver.objects(City_id=cityID).values_list('Driver_ID'))
    routehistoryList = routehistory.objects(D_id__in=driverList)
    result = RouteHistorySerializer(routehistoryList,many=True)
    response = {}
    response['data']= result.data
    response["Access-Control-Allow-Origin"] = "*"
    return JsonResponse(response)
