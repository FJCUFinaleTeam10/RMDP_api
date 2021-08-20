# Create your views here.
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from .models import driver
from .serializers import DriverSerializer


# Create your views here.
@api_view(['POST'])
def listAll(request):
    offset = int(request.data['params']['skip'])
    items_per_page = int(request.data['params']['limit'])
    driverList = driver.objects.skip(offset).limit(items_per_page)
    result = DriverSerializer(driverList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response
