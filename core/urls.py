from django.contrib import admin
from django.urls import path

from driver.views import listAll, getDriverBaseOnCity
from geolocation.views import getAllCountryCode, getAllCities, getCountryCode, getCities
from menu.views import getMenu, getMenuBaseOnRestaurant
from order.views import createOrder, getOrderBaseOnCity
from restaurant.views import listAllRestaurantList, getRestaurantBaseOnId, getRestaurantBaseOnCity, listRestaurantList
from rmdp_env.views import listAllSetting, getSettingBaseOneCity, updateSetting
from q_learning.views import  getQlearningBaseOnCity
urlpatterns = [
    path('admin/', admin.site.urls, name='index'),

    path('driver/getalldriver/', listAll, name='index'),
    path('driver/getdriverbaseoncity/', getDriverBaseOnCity, name='index'),

    path('restaurant/getallrestaurantlist', listAllRestaurantList, name='index'),
    path('restaurant/getrestaurantlist/', listRestaurantList, name='index'),
    path('restaurant/getrestaurantbaseoncity/', getRestaurantBaseOnCity, name='index'),
    path('restaurant/getrestaurantbaseonid/', getRestaurantBaseOnId, name='index'),

    path('order/listAll/', listAll, name='index'),
    path('order/createOrder/', createOrder, name='index'),
    path('order/baseoncity/', getOrderBaseOnCity, name='index'),

    path('getMenu/', getMenu, name='index'),
    path('baseonrestaurant/', getMenuBaseOnRestaurant, name='index'),

    path('geolocation/getcity/', getCities),
    path('geolocation/getallcountrycode/', getAllCountryCode),
    path('geolocation/getCountryCode/', getCountryCode),
    path('geolocation/getallcities/', getAllCities),

    path('envsetting/getallsetting/', listAllSetting),
    path('envsetting/getsettingbaseoncity/', getSettingBaseOneCity),
    path('envsetting/updatesetting/', updateSetting),

    path('qlearning/getqlearningbaseoncity/', getQlearningBaseOnCity),
]
