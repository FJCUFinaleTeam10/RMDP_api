from django.urls import path
from .views import *

urlpatterns = [
    path('getcity/', getCities),
    path('getallcountrycode/', getAllCountryCode),
    path('getCountryCode/', getCountryCode),
    path('getallcities/', getAllCities)
]
