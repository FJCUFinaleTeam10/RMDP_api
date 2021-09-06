from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls, name='index'),
    path('driver/', include('RMDP_api.apps.driver.urls'), name='index'),
    path('restaurant/', include('RMDP_api.apps.restaurant.urls'), name='index'),
    path('order/', include('RMDP_api.apps.order.urls'), name='index'),
    path('menu/', include('RMDP_api.apps.menu.urls'), name='index'),
    path('geolocation/', include('RMDP_api.apps.geolocation.urls'), name='index')
]
