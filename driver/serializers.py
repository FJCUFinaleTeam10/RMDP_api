from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import driver
from .models import test_driver


class DriverSerializer(DocumentSerializer):
    class Meta:
        model = driver
class GenerateDriverSerializer(DocumentSerializer):
    class Meta:
        model = test_driver
