from django.urls import include, path
from .views import *

urlpatterns = [
    path('getallrestaurantlist', listAllRestaurantList, name='index'),
    path('getrestaurantlist/', listRestaurantList,name='index'),
    path('getrestaurantbaseoncity/', getRestaurantBaseOnCity,name='index'),
    path('getrestaurantbaseonid/', getRestaurantBaseOnId,name='index'),
]
