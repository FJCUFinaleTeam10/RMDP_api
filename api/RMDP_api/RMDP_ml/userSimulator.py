# from generatingData import generateTestData
# from Math.Geometry import interSectionCircleAndLine
import threading
from datetime import date
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

        self.client = MongoClient('mongodb://admin:admin@mongodb:27017/RMDP?authSource=admin')
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
        url = 'http://localhost:8000/order/createOrder/'  # Set destination URL here
        generatedLocation = self.generateLocation(currentCity['Longitude'], currentCity['Latitude'],
                                                  currentCity['radius'])
        filteredRestaurant = list(self.restaurantCollection.find({"City": currentCity['City']}, {'Restaurant_ID': 1}))
        post_fields = {
            'longitude': generatedLocation[0],
            'latitude': generatedLocation[1],
            'requestTime': date.today(),
            'restaurantId': filteredRestaurant[random.randint(0, len(filteredRestaurant)-1)]['Restaurant_ID'],
            'totalPrice:': random.uniform(1.0, 1000.0),
            'firstName': "test firstName" + str(index),
            'lastName': "test lastName" + str(index),
            ' email': "testEmail" + str(index) + '@gmail.com',
            'description': "test description",
            'telephone': "0123456789",
        }  # Set POST fields here
        request = Request(url, urlencode(post_fields).encode())
        json = urlopen(request).read().decode()
        print(json)

    def generateLocation(self, Longitude, Latitude, Radius):
        return [random.uniform(float(Latitude), float(Latitude) + float(Radius)),
                random.uniform(float(Longitude), float(Longitude) + float(Radius))]


test = userSimulator()
test.generateThread()
