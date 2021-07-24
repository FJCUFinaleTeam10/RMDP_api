# Create your views here.
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from .models import driver
from .serializers import DriverSerializer


# Create your views here.
@api_view(['GET', 'POST', 'DELETE'])
def listAll(request):
    if request.method == 'GET':
        driverList = driver.objects.all()
        result = DriverSerializer(driverList, many=True)
        response=JsonResponse(result.data, safe=False)
        return response
    if request.method == 'POST':
        pass
    if request.method == 'DELETE':
        pass
