from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import driver


class DriverSerializer(DocumentSerializer):
    class Meta:
        model = RMP_env

