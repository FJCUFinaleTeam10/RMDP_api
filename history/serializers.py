from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework_mongoengine.serializers import DocumentSerializer
from geolocation.models import *
from history.models import history


class HistorySerializer(DocumentSerializer):

    # @property
    # def data(self):
    #     ret = super(HistorySerializer, self).data
    #     return ReturnDict(ret, serializer=self)
    #
    # # In class ReturnDict(OrderedDict)
    # def __init__(self, *args, **kwargs):
    #     self.serializer = kwargs.pop('serializer')
    #     super(ReturnDict, self).__init__(*args, **kwargs)

    class Meta:
        model = history