from rest_framework_mongoengine.serializers import DocumentSerializer
from rmdp_env.models import rmdp_env


class OrderSerializer(DocumentSerializer):
    class Meta:
        model = rmdp_env
