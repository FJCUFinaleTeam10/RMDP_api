from django.urls import path
from .views import *

urlpatterns = [
    path('getCity/', getCities),
    path('getallcountrycode/', getAllCountryCode),
    path('getCountryCode/', getCountryCode),
    path('getallcities/', getAllCities)
]
