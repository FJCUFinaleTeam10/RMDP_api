from django.urls import include, path
from .views import *

urlpatterns = [
    path('', listAll, name='index'),
    path('getRestaurantList/', getRestaurantList, name='index'),
]
