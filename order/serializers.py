from rest_framework_mongoengine.serializers import DocumentSerializer
from order.models import order


class OrderSerializer(DocumentSerializer):
    class Meta:
        model = order