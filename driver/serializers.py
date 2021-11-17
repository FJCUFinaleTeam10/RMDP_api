from rest_framework_mongoengine.serializers import DocumentSerializer
from driver.models import driver


class DriverSerializer(DocumentSerializer):
    class Meta:
        model = driver
        fields = '__all__'


class GenerateDriverSerializer(DocumentSerializer):
    class Meta:
        model = driver
        fields = '__all__'
