# Create your views here.
import json

from bson import json_util
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from mongoengine import MultipleObjectsReturned
from requests import Response
from rest_framework.decorators import api_view

from driver.models import driver
from driver.serializers import DriverSerializer


# Create your views here.
@api_view(['POST'])
def listAll(request):
    driverList = driver.objects.all()
    result = DriverSerializer(driverList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


@api_view(['POST', 'OPTIONS'])
def getDriverBaseOnCity(request,format = None):
    try:
        cityID = request.data.get('cityId', 1)
        skip = request.data.get('skip', 0)
        limit = request.data.get('limit', 9999999)
        driverList = driver.objects(City_id=cityID).skip(skip).limit(limit)
        totalValue = driver.objects(City_id=cityID).count()
        result = DriverSerializer(driverList, many=True)
        response = {}
        response["Access-Control-Allow-Origin"] = "*"
        response['count'] = totalValue
        response['data'] = json.loads(json_util.dumps(result.data))
        return JsonResponse(response)
    except IntegrityError as IE:
        print(IE)
    except MultipleObjectsReturned as ME:
        print(ME)
    except Exception as e:
        print(e)


@api_view(['POST'])
def getDriverIDBaseOnCity(request):
    try:
        cityID = request.data['params'].get('cityId', 1)
        driverList = driver.objects(City_id=cityID).only('Driver_ID')
        totalValue = driver.objects(City_id=cityID).count()
        result = DriverSerializer(driverList, many=True)
        response = {}
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST"
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


@api_view(['POST'])
def getDriverBaseOnID(request):
    try:
        driverID = int(request.data['params'].get('driverId', None))

        driverList = driver.objects(Driver_ID=driverID)
        result = DriverSerializer(driverList, many=True)
        response = JsonResponse(json.loads(json_util.dumps(result.data)), safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return response
    except IntegrityError as IE:
        print(IE)
    except MultipleObjectsReturned as ME:
        print(ME)
    except Exception as e:
        print(e)
