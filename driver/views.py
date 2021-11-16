# Create your views here.
import json

from bson import json_util
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from mongoengine import MultipleObjectsReturned
from rest_framework.decorators import api_view

from .models import driver
from .serializers import DriverSerializer, GenerateDriverSerializer


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


@api_view(['POST'])
def getDriverBaseOnCity(request):
    try:
        filterSet = request.data['params']
        cityName = filterSet.get('city', 'Agra')
        cityID = filterSet.get('cityId', 1)
        skip = filterSet.get('skip', 0)
        limit = filterSet.get('limit', 1000)
        driverList = driver.objects(City_id=cityID).skip(skip).limit(limit)
        result = DriverSerializer(driverList, many=True)
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
        raise IE
    except MultipleObjectsReturned as ME:
        raise ME
    except Exception as e:
        raise e