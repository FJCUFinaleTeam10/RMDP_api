from django.http import JsonResponse
from rest_framework.decorators import api_view

from menu.models import menu
from menu.serializers import MenuSerializer


@api_view(['POST'])
def getMenu(request):
    offset = int(request.data['params']['skip'])
    items_per_page = int(request.data['params']['limit'])
    restId = int (request.data['params']['restId'])
    menuList = menu.objects(restaurant_id = restId).skip(offset).limit(items_per_page)
    result = MenuSerializer(menuList, many=True)
    response = JsonResponse(result.data, safe=False)
    return response


@api_view(['POST'])
def getMenuBaseOnRestaurant(request):
    try:
        rest_id = request.data['restId']
        menuList = menu.objects(restaurant_id=rest_id)
        result = MenuSerializer(menuList, many=True)
        response = JsonResponse(result.data, safe=False)
        return response
    except Exception:
        print(Exception)