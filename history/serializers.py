from rest_framework_mongoengine.serializers import DocumentSerializer
from geolocation.models import *
from history.models import history


class HistorySerializer(DocumentSerializer):
    class Meta:
        model = history