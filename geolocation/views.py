from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import *
from .serializers import *


# Create your views here.

# Create your views here.
@api_view(['GET'])
def getAllCountryCode(request):
    countryCodeList = country_code.objects.all()
    result = countrySerializer(countryCodeList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response

@api_view(['POST'])
def getCountryCode(request):
    offset = int(request.data['params']['skip'])
    items_per_page = int(request.data['params']['limit'])
    countryList = country_code.objects.skip(offset).limit(items_per_page)
    result = countrySerializer(countryList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


# Create your views here.
@api_view(['POST'])
def getCities(request):
    offset = int(request.data['params']['skip'])
    items_per_page = int(request.data['params']['limit'])
    cityList = all_cities.objects.skip(offset).limit(items_per_page)
    result = CitySerializer(cityList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


@api_view(['GET'])
def getAllCities(request):
    cityList = all_cities.objects.all()
    result = CitySerializer(cityList, many=True)
    response = JsonResponse(result.data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response


