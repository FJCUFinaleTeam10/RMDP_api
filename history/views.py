from dateutil import parser
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework.decorators import api_view

from driver.models import driver
from history.models import history
from history.serializers import HistorySerializer
from geolocation.serializers import *
from rest_framework_mongoengine import serializers


@api_view(['POST'])
def getHistoryBaseOnCityList(request):
    try:
        cityID = int(request.data['params'].get('cityID', None))
        method = int(request.data['params'].get('method', None))
        method+=1
        fromDate = parser.parse(request.data['params'].get('from', None))
        toDate = parser.parse(request.data['params'].get('to', None))
        driverList = list(driver.objects(City_id=cityID).values_list('Driver_ID'))
        response = {}
        historyList = history.objects(
            Q(D_id__in=driverList) & Q(Time__gte=fromDate) & Q(Time__lte=toDate) & Q(Method=method))
        result = HistorySerializer(historyList, many=True)
        # json_data = [ob.to_mongo() for ob in historyList]
        # response['data'] = serializers.serialize("json",historyList, many=True)
        # response['data'] = dict(map(lambda driverID:(str(driverID),HistorySerializer(history.objects(D_id=driverID), many=True).data),driverList))
        response["Access-Control-Allow-Origin"] = "*"
        response['data'] = result.data
        response['driverList'] = driverList
        return JsonResponse(response)
    except IntegrityError:
        print(IntegrityError)
    except MultipleObjectsReturned:
        print(MultipleObjectsReturned)
    except Exception as e:
        raise print(e)
