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
        for currentDriver in list(driver for driver in driverList if len(Mongo_Operator.getDriverRouteBaseOnDriverID(driver[0])) > 0):  # get driver route > 0 in list
            driverRoute = Mongo_Operator.getDriverRouteBaseOnDriverID(currentDriver[0])
            targetDestination = next(node for node in driverRoute if node[6]==1)
            # distance between target distance and current driver
            DistanceRemain = Geometry.coorDistance(currentDriver[4],
                                                   currentDriver[3],
                                                   targetDestination[1],
                                                   targetDestination[2])
            # the distance of each update time
            DistanceTraveled = (currentDriver[5] * updateTime) / 1000
            # transform distance to degree
            # the driver update distance longer than next destination
            if DistanceTraveled >= DistanceRemain:
                currentDriver[4] = targetDestination[1]
                currentDriver[3] = targetDestination[2]
                deleteindex = np.where(driverRoute==targetDestination)
                driverRoute = np.delete(driverRoute,deleteindex)
                currentOrder = next(iter(Mongo_Operator.getPairedOrderBaseOnOrderID(targetDestination[4],targetDestination[5])))
                if targetDestination[3] == 1:
                    currentOrder[12] = 4
                    currentDriver[6] -= 1
                    currentOrder[6] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                else:
                    currentOrder[12] = 3
                    currentOrder[10] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                # self.DBclient.updateOrder(targetDestination)
                Mongo_Operator.updateOrder(currentOrder)
                if len(driverRoute) ==0:
                    currentDriver[5] = 0
                targetDestination[7] = 1
                Mongo_Operator.updateRoute(targetDestination)
                driverRoute[:][6]-=1
            else:
                updatedLat, updatedLon = Geometry.interSectionCircleAndLine(currentDriver[4],
                                                                            currentDriver[3],
                                                                            DistanceTraveled / 1000,
                                                                            currentDriver[4],
                                                                            currentDriver[3],
                                                                            targetDestination[1],
                                                                            targetDestination[2])

                currentDriver[4] = updatedLat
                currentDriver[3] = updatedLon
                # logging.info("updateded")
            '''
            aftterDIstance = Geometry.coorDistance(currentDriver[4],
                                                   currentDriver[3],
                                                   targetDestination[1],
                                                   targetDestination[2])
            '''
            Mongo_Operator.updateDriver(currentDriver)
            for route in driverRoute:
                Mongo_Operator.updateRoute(route)
    except Exception as e:
        logging.critical(e, exc_info=True)