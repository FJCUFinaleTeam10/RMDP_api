from django.urls import path
from .views import *

urlpatterns = [
    path('getCities/', getCities),
    path('getAllCities/', getAllCities),
    path('',)
]
