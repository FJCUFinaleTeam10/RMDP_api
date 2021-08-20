from rest_framework_mongoengine.serializers import DocumentSerializer

from menu.models import menu


class MenuSerializer(DocumentSerializer):
    class Meta:
        model = menu
        fields = '__all__'
