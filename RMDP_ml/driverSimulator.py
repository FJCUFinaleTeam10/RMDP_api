import logging
import os
from datetime import datetime

import numpy as np

from RMDP_ml.Math import Geometry
from RMDP_ml.Database_Operator import Mongo_Operator

totalCurrentWorker = 2
DEBUG = False if int(os.environ['DEBUG']) == 1 else True
updateTime = 1


def generateThread():
    logging.info("start generating")
    cityList = Mongo_Operator.getAllCity()
    np.apply_along_axis(updateDriverLocation, axis=1, arr=cityList)


def updateDriverLocation(city):
    try:
        #rawData['City_id'] == 0
        #rawData['Country_Code'] == 1
        #rawData['Latitude']  == 2
        #rawData['Longitude']  == 3
        #rawData['radius']  == 4
        driverList = Mongo_Operator.getHasOrderDriverBaseOnCity(city[0])
        for currentDriver in list(
                driver for driver in driverList if len(driver['Route']) > 0):  # get driver route > 0 in list
            targetDestination = currentDriver['Route'][0]
            # distance between target distance and current driver
            DistanceRemain = Geometry.coorDistance(currentDriver['Latitude'],
                                                   currentDriver['Longitude'],
                                                   targetDestination['Latitude'],
                                                   targetDestination['Longitude'])
            # the distance of each update time
            DistanceTraveled = (currentDriver['Velocity'] * updateTime) / 1000
            # transform distance to degree
            # the driver update distance longer than next destination
            if DistanceTraveled >= DistanceRemain:
                currentDriver['Latitude'] = targetDestination['Latitude']
                currentDriver['Longitude'] = targetDestination['Longitude']
                travelLocation = currentDriver['Route'].pop(0)
                currentOrder = next(iter(Mongo_Operator.getPairedOrderBaseOnOrderID(travelLocation['Order_ID'])))
                if travelLocation['nodeType'] == 1:
                    currentOrder['order_status'] = 'delivered'
                    currentDriver['Capacity'] -= 1
                    currentOrder['order_delivered_customer_date'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                else:
                    currentOrder['order_status'] = 'headToCus'
                    currentOrder['order_restaurant_carrier_date'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                # self.DBclient.updateOrder(targetDestination)
                Mongo_Operator.updateOrder(currentOrder)
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
            print(DistanceRemain, " ", aftterDIstance)
            Mongo_Operator.updateDriver(currentDriver)
    except Exception as e:
        logging.critical(e, exc_info=True)