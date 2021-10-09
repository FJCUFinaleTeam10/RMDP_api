from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import *


class CitySerializer(DocumentSerializer):
    class Meta:
        model = all_cities


class countrySerializer(DocumentSerializer):
    class Meta:
        model = country_code
