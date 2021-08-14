from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import driver
from .models import Generate_Driver


class DriverSerializer(DocumentSerializer):
    class Meta:
        model = driver
        fields = '__all__'


class GenerateDriverSerializer(DocumentSerializer):
    class Meta:
        model = Generate_Driver
        fields = '__all__'
