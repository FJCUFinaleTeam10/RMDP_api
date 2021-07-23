from django.urls import path
from .views import listAll

urlpatterns = [
    path('', listAll),
]
