from rest_framework_mongoengine.serializers import DocumentSerializer
from rmdp_env.models import rmdp_env


class RMDP_envSerializer(DocumentSerializer):
    class Meta:
        model = rmdp_env
        fields = '__all__'

