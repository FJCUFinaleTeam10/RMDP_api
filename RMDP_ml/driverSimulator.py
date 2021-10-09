# from generatingData import generateTestData
# from Math.Geometry import interSectionCircleAndLine
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
# from Math import Geometry

from Database_Operator.Mongo_Operator import Mongo_Operate
from Math import Geometry


class driverSimulator:
    def __init__(self):
        self.totalCurrentWorker = 2
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
        self.DBclient = Mongo_Operate()
        self.updateTime = 1

    def generateThread(self):
        cityList = self.DBclient.getAllCity()  # get all city
        totalCurrentWorker = 81
        logging.info("start generating")
        with ThreadPoolExecutor(max_workers=totalCurrentWorker) as executor:
            threads = []
            for i in range(len(cityList)):
                threads.append(executor.submit(self.updateDriverLocation, cityName=(cityList[i]['City'])))
        logging.info("task completed")

    def updateDriverLocation(self, cityName):
        try:
            driverList = self.DBclient.getHasOrderDriverBaseOnCity(cityName)
            for currentDriver in (driver for driver in driverList if len(driver['Route']) > 0):
                targetDestination = currentDriver['Route'][0]
                # distance between target distance and current driver

                DistanceRemain = Geometry.coorDistance(currentDriver['Latitude'],
                                                       currentDriver['Longitude'],
                                                       targetDestination['Latitude'],
                                                       targetDestination['Longitude'])
                # the distance of each update time
                DistanceTraveled = (currentDriver['Velocity'] * self.updateTime) / 1000
                # transform distance to degree
                # the driver update distance longer than next destination
                if DistanceTraveled >= DistanceRemain:
                    currentDriver['Latitude'] = targetDestination['Latitude']
                    currentDriver['Longitude'] = targetDestination['Longitude']
                    travelLocation = currentDriver['Route'].pop(0)
                    currentOrder = next(iter(self.DBclient.getPairedOrderBaseOnOrderID(travelLocation['Order_ID'])))
                    if travelLocation['nodeType'] == 0:
                        currentOrder['order_status'] = 'delivered'
                        currentDriver['Capacity'] -= 1
                        currentOrder['order_delivered_customer_date'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    else:
                        currentOrder['order_status'] = 'headToCus'
                        currentOrder['order_restaurant_carrier_date'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    self.DBclient.updateOrder(targetDestination)
                    if currentDriver['Route'] is None:
                        currentDriver['Velocity'] = 0
                else:
                    updatedLat, updatedLon = Geometry.interSectionCircleAndLine(currentDriver['Latitude'],
                                                                                currentDriver['Longitude'],
                                                                                DistanceTraveled / 1000,
                                                                                currentDriver['Latitude'],
                                                                                currentDriver['Longitude'],
                                                                                targetDestination['Latitude'],
                                                                                targetDestination['Longitude'])

                    currentDriver['Latitude'] = updatedLat
                    currentDriver['Longitude'] = updatedLon
                    # logging.info("updateded")
                aftterDIstance = Geometry.coorDistance(currentDriver['Latitude'],
                                                       currentDriver['Longitude'],
                                                       targetDestination['Latitude'],
                                                       targetDestination['Longitude'])
                print(DistanceRemain," ",aftterDIstance)
                self.DBclient.updateDriver(currentDriver)
        except Exception as e:
            logging.critical(e, exc_info=True)
