# Create your views here.
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from .models import driver, test_driver
from .serializers import DriverSerializer, GenerateDriverSerializer

# Create your views here.
@api_view(['GET'])
def listAll(request):
    if request.method == 'GET':
        driverList = driver.objects.all()
        result = DriverSerializer(driverList, many=True)
        response = JsonResponse(result.data, safe=False)
        return response


# Create your views here.
@api_view(['GET'])
def listAllGenerateDriver(request):
    if request.method =='GET':
        driverList = test_driver.objects.all()
        result =  GenerateDriverSerializer(driverList, many=True)
        response = JsonResponse(result.data, safe=False)
        return response
