from rest_framework_mongoengine.serializers import DocumentSerializer
from q_learning.models import q_learning


class Q_learningSerializer(DocumentSerializer):
    class Meta:
        model = q_learning