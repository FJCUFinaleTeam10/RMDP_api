from django.shortcuts import render

# Create your views here.
from driver.models import driver
from driver.serializers import DriverSerializer
from rest_framework import viewsets


# Create your views here.
class DriverViewSet(viewsets.ModelViewSet):
    queryset = driver.objects.all()
    serializer_class = DriverSerializer
