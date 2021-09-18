from django.urls import path
from .views import *

urlpatterns = [
    path('getalldriver/', listAll),
    path('getdriverbaseoncity/', getDriverBaseOnCity),
]
