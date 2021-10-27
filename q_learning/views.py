import logging

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view
from q_learning.models import q_learning
from q_learning.serializers import QlearningSerializer
from mongoengine.base import get_document as get_model

# Create your views here.


@api_view(['POST'])
def getQlearningBaseOnCity(request):
    try:
        filterSet = request.data['params']
        cityName = filterSet.get('city', 'Agra')
        q_learningList = q_learning.objects(City=cityName)
        result = QlearningSerializer(q_learningList, many=True)
        response = JsonResponse(result.data, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        logging.ERROR