from django.urls import include, path
from .views import *
urlpatterns = [
    path('listAll/', listAll, name='index'),
    path('createOrder/', createOrder, name='index'),
]
