# Create your views here.
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from .models import driver
from .serializers import DriverSerializer, GenerateDriverSerializer


# Create your views here.
@api_view(['POST'])
def listAll(request):
    driverList = driver.objects.all()
    result = DriverSerializer(driverList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response


@api_view(['POST'])
def getDriverBaseOnCity(request):
    cityName = request.data['params']['city']
    driverList = driver.objects(City=cityName)
    result = DriverSerializer(driverList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response
