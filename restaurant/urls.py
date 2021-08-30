from django.urls import include, path
from .views import *

urlpatterns = [
    path('getallrestaurantlist', listAllRestaurantList, name='index'),
    path('getrestaurantbaseoncity/', getRestaurantBaseOnCity,name='index'),
]
