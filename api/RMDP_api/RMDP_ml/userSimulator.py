# from generatingData import generateTestData
# from Math.Geometry import interSectionCircleAndLine
import threading
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

        self.client = MongoClient('mongodb://admin:admin@localhost:27017/RMDP?authSource=admin')
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
            threads.append(threading.Thread(target=self.generateOrder(), args=(i,cityList[i],)))
            threads[i].start()
        for i in range(len(cityList)):
            threads[i].join()

    def generateOrder(self,index,currentCity):
        url = 'https://localhost:8000/order/createOrder/'  # Set destination URL here
        post_fields = {
            'longitude': currentCity.Longitude,
            'latitude': currentCity.Latitude,
            'requestTime': "",
            'restaurantId': current,
            'totalPrice:': ,
            'firstName': "test firstName"+index,
            'lastName': "test lastName"+index,
            ' email': "testEmail",
            'description': "test description",
            'telephone': "0123456789",
        }  # Set POST fields here
        request = Request(url, urlencode(post_fields).encode())
        json = urlopen(request).read().decode()
        print(json)

test = RMDP()
test.generateThread()
