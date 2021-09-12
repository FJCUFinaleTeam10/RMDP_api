# from generatingData import generateTestData
# from Math.Geometry import interSectionCircleAndLine
import os
import threading
from datetime import date, datetime
import random
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from pymongo import MongoClient


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


def mongoClientUrl(DEBUG):
    if DEBUG:
        return "mongodb://admin:admin@localhost:27017/RMDP?authSource=admin"
    else:
        return "mongodb://admin:admin@mongodb:27017/RMDP?authSource=admin"


class userSimulator:
    _instance = None

    def __init__(self):
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
        # self.DEBUG = True
        self.client = MongoClient(mongoClientUrl(self.DEBUG))
        self.databaseName = self.client["RMDP"]
        self.restaurantCollection = self.databaseName["restaurant"]
        self.driverCollection = self.databaseName["driver"]
        self.all_citiesCollection = self.databaseName["all_cities"]
        self.country_codeCollection = self.databaseName["country_code"]
        self.orderCollection = self.databaseName["order"]

    def generateThread(self):
        cityList = list(self.all_citiesCollection.find())
        threads = []
        for i in range(len(cityList)):
            threads.append(threading.Thread(target=self.generateOrder, args=(i, cityList[i],)))
            threads[i].start()
        for i in range(len(cityList)):
            threads[i].join()

    def generateOrder(self, index, currentCity):
        try:
            generatedLocation = self.generateLocation(currentCity['Longitude'], currentCity['Latitude'],
                                                      currentCity['radius'])
            filteredRestaurant = list(
                self.restaurantCollection.find({"City": currentCity['City']}, {'Restaurant_ID': 1}))
            self.orderCollection.insert({
                'order_approved_at': None,
                'order_customer_Longitude': generatedLocation[1],
                'order_customer_Latitude': generatedLocation[0],
                'order_delivered_customer_date': None,
                'order_request_time': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                'order_restaurant_carrier_date': None,
                'order_restaurant_carrier_restaurantId':
                    filteredRestaurant[random.randint(0, len(filteredRestaurant) - 1)]['Restaurant_ID'],
                'driver_id': None,
                'order_status': 'unasgined'
            })
        except ValueError:
            print(ValueError)

    def generateLocation(self, Longitude, Latitude, Radius):
        return [random.uniform(float(Latitude), float(Latitude) + float(Radius)),
                random.uniform(float(Longitude), float(Longitude) + float(Radius))]


test = userSimulator()
test.generateThread()
