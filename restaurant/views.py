from django.shortcuts import render

# Create your views here.
from restaurant.models import restaurant
from restaurant.serializers import RestaurantSerializer
from rest_framework import viewsets


# Create your views here.
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = restaurant.objects.all()
    serializer_class = RestaurantSerializer
