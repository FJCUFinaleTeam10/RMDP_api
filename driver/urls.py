from django.urls import path
from .views import listAll
from .views import listAllGenerateDriver
urlpatterns = [
    path('', listAll),
    path('generatedDriver/',listAllGenerateDriver)
]
