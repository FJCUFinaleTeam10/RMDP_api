from django.contrib import admin
from django.urls import include, path
from driver import urls as driver_urls
from order import urls as order_urls
from restaurant import urls as restaurant_urls
from menu import urls as menu_urls
from geolocation import urls as geolocation_urls

urlpatterns = [
    path('', driver_urls, name="upload"),
    path('admin/', admin.site.urls, name='index'),
    path('driver/', driver_urls, name='index'),
    path('restaurant/', restaurant_urls, name='index'),
    path('order/', order_urls, name='index'),
    path('menu/', menu_urls, name='index'),
    path('geolocation/', geolocation_urls, name='index'),
]
