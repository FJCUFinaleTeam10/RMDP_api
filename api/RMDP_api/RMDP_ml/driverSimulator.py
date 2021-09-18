# from generatingData import generateTestData
# from Math.Geometry import interSectionCircleAndLine
import logging
import os
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
import random
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from pymongo import MongoClient
# from Math import Geometry
# from Database_Operator.Mongo_Operator import Mongo_Operate


class driverSimulator:
    _instance = None

    def __init__(self):

        self.totalCurrentWorker = 2
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else False
        self.client = self.getMongoClientUrl(self.DEBUG)
        self.databaseName = self.client["RMDP"]
        self.restaurantCollection = self.databaseName["restaurant"]
        self.driverCollection = self.databaseName["driver"]
        self.all_citiesCollection = self.databaseName["all_cities"]
        self.country_codeCollection = self.databaseName["country_code"]
        self.orderCollection = self.databaseName["order"]

    def generateThread(self):

        cityList = self.MongoClient.getAllCity()
        logging.info("start generating city")
        with ThreadPoolExecutor(max_workers=self.totalCurrentWorker) as executor:
            threads = []
            for i in range(len(cityList)):
                threads.append(executor.submit(self.updateDriverLocation, index=i, cityName=(cityList[i]['City'])))
        logging.info("task completed")

    def updateDriverLocation(self, time, cityName):
        driverList = list(self.driverCollection.find({"City": cityName}))
        # orderList =
        hasOrderVehicle: list = [routePerVehicle for routePerVehicle in self.Theta_x if
                                 (routePerVehicle['route'] != [])]

        for route in hasOrderVehicle:
            currentDriver = self.vehiceList[route.get("driverId") - 1]
            targetDestination = route['route'][0]
            travledDistance = currentDriver.getVelocity() * time
            estimatedDistance = self.coorDistance(currentDriver.getLatitude(), currentDriver.getLongitude(),
                                                      targetDestination.getLatitude(), targetDestination.getLongitude())
            if travledDistance > 0:

                if travledDistance >= estimatedDistance:
                    currentDriver.setLatitude(targetDestination.getLatitude())
                    currentDriver.setLongitude(targetDestination.getLongitude())
                    route['route'].pop(0)
                else:
                    updatedLon, updatedLat = self.Geometry.interSectionCircleAndLine(currentDriver.getLongitude(),
                                                                                currentDriver.getLatitude(),
                                                                                travledDistance,
                                                                                currentDriver.getLongitude(),
                                                                                currentDriver.getLatitude(),
                                                                                targetDestination.getLongitude(),
                                                                                targetDestination.getLatitude())
                    currentDriver.setLatitude(updatedLon)
                    currentDriver.setLongitude(updatedLat)


test = driverSimulator()
test.generateThread()
