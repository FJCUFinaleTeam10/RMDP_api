from rest_framework_mongoengine.serializers import DocumentSerializer
from routehistory.models import routehistory


class RouteHistorySerializer(DocumentSerializer):
    class Meta:
        model = routehistory
        fields = '__all__'
