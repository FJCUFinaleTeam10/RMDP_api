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
        # rawData['City_id'] == 0
        # rawData['Country_Code'] == 1
        # rawData['Latitude']  == 2
        # rawData['Longitude']  == 3
        # rawData['radius']  == 4

        driverList = Mongo_Operator.getHasOrderDriverBaseOnCity(city[0])
        for currentDriver in list(driver for driver in driverList if Mongo_Operator.getDriverRouteBaseOnDriverID(driver[0]).size > 0) : # get driver route > 0 in list
            storageRoute = np.zeros(shape=(0, 8))
            driverRoute = Mongo_Operator.getDriverRouteBaseOnDriverID(currentDriver[0])
            if driverRoute.size<1:
                continue
            driverRoute = driverRoute[driverRoute[:, 6].argsort()]
            DistanceRemain = Geometry.coorDistance(currentDriver[4], currentDriver[3], driverRoute[0][1],driverRoute[0][2])
            # the distance of each update time
            DistanceTraveled = (currentDriver[5] * updateTime) / 1000
            # transform distance to degree
            # the driver update distance longer than next destination
            if DistanceTraveled >= DistanceRemain:
                currentDriver[4] = driverRoute[0][1]
                currentDriver[3] = driverRoute[0][2]

                currentOrder = next(iter(Mongo_Operator.getPairedOrderBaseOnOrderID(driverRoute[0][5])))
                if driverRoute[0][3] == 1:
                    currentOrder[12] = 4
                    currentDriver[6] -= 1
                    currentOrder[6] = datetime.now()
                else:
                    currentOrder[12] = 3
                    currentOrder[10] = datetime.now()
                # self.DBclient.updateOrder(targetDestination)
                Mongo_Operator.updateOrder(currentOrder)
                storageRoute = np.row_stack((storageRoute, driverRoute[0]))
                driverRoute = np.delete(driverRoute, 0, axis=0)

                if len(driverRoute) == 0:
                    currentDriver[5] = 0
                storageRoute[0][7] = 1
                driverRoute[...,6]-=1
                Mongo_Operator.updateRoute(storageRoute[0])
            else:
                updatedLat, updatedLon = Geometry.interSectionCircleAndLine(currentDriver[4],
                                                                            currentDriver[3],
                                                                            DistanceTraveled / 1000,
                                                                            currentDriver[4],
                                                                            currentDriver[3],
                                                                            driverRoute[0][1],
                                                                            driverRoute[0][2])

                currentDriver[4] = updatedLat
                currentDriver[3] = updatedLon
            Mongo_Operator.updateDriver(currentDriver)
            for route in driverRoute:
                Mongo_Operator.updateRoute(route)
    except Exception as e:
        logging.critical(e, exc_info=True)

