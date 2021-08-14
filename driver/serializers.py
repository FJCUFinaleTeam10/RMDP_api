from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import driver
from .models import testdriver


class DriverSerializer(DocumentSerializer):
    class Meta:
        model = driver
class GenerateDriverSerializer(DocumentSerializer):
    class Meta:
        model = testdriver
