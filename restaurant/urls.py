from django.urls import include, path
from .views import listAll

urlpatterns = [

    path('', listAll, name='index')
]
