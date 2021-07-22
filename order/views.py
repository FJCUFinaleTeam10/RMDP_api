from django.shortcuts import render

# Create your views here.
from order.models import order
from order.serializers import OrderSerializer
from rest_framework import viewsets


# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = order.objects.all()
    serializer_class = OrderSerializer
