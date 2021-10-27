from rest_framework_mongoengine.serializers import DocumentSerializer
from q_learning.models import q_learning


class QlearningSerializer(DocumentSerializer):
    class Meta:
        model = q_learning