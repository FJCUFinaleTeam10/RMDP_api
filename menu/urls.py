from django.urls import include, path
from .views import *

urlpatterns = [
    path('getMenu/', getMenu, name='index')
]
