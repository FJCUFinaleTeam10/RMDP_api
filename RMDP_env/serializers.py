from rest_framework_mongoengine.serializers import DocumentSerializer
from RMDP_env.models import RMDP_env


class RMDP_envSerializer(DocumentSerializer):
    class Meta:
        model = RMDP_env
        fields = '__all__'

