from dateutil.parser import parser
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework.decorators import api_view

from driver.models import driver
from history.models import history
from history.serializers import HistorySerializer
from geolocation.serializers import *


@api_view(['POST'])
def getHistoryBaseOnCityList(request):
    cityID = int(request.data['params'].get('cityID', None))
    fromDate = parser.parse(request.data['params'].get('from', None))
    toDate = parser.parse(request.data['params'].get('to', None))
    driverList = list(driver.objects(City_id=cityID).values_list('Driver_ID'))
    routehistoryList = history.objects(D_id__in=driverList)
    result = HistorySerializer(routehistoryList, many=True)
    response = {}
    response['data'] = result.data
    response["Access-Control-Allow-Origin"] = "*"
    return JsonResponse(response)
