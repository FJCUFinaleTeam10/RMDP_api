from rest_framework_mongoengine.serializers import DocumentSerializer
from route.models import route


class RouteSerializer(DocumentSerializer):
    class Meta:
        model = route
        fields = '__all__'