from django.urls import include, path
from .views import listAll
from .views import createOrder

urlpatterns = [
    path('listAll/', listAll, name='index'),
    path('createOrder/', createOrder, name='index'),
]
