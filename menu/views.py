from django.http import JsonResponse
from rest_framework.decorators import api_view

from .models import menu
from .serializers import MenuSerializer


@api_view(['POST'])
def getMenu(request):
    offset = int(request.data['params']['skip'])
    items_per_page = int(request.data['params']['limit'])
    menuList = menu.objects.skip(offset).limit(items_per_page)
    result = MenuSerializer(menuList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response


@api_view(['POST'])
def getMenuBaseOnRestaurant(request):
    rest_id = request.data['restId']
    menuList = menu.objects(restaurant_id=rest_id)
    result = MenuSerializer(menuList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response
