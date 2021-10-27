# Create your views here.
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from rmdp_env.models import rmdp_env
from rmdp_env.serializers import RMDP_envSerializer


# Create your views here.
@api_view(['GET'])
def listAllSetting(request):
    settingList = rmdp_env.objects.all()
    result = RMDP_envSerializer(settingList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response


@api_view(['POST'])
def updateSetting(request):
    settingList = rmdp_env.objects.all()
    result = RMDP_envSerializer(settingList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response

@api_view(['POST'])
def getSettingBaseOneCity(request):
    cityName = request.data['city']
    settingList = rmdp_env.objects(City=cityName)
    result = RMDP_envSerializer(settingList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response