from django.http import JsonResponse, HttpResponse
# Create your views here.
from rest_framework.decorators import api_view

from order.models import order
from order.serializers import OrderSerializer


# Create your views here.
@api_view(['GET', 'POST', 'DELETE'])
def listAll(request):
    if request.method == 'GET':
        orderList = order.objects.all()
        result = OrderSerializer(orderList, many=True)
        response = JsonResponse(result.data, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    if request.method == 'POST':
        pass
    if request.method == 'DELETE':
        pass
