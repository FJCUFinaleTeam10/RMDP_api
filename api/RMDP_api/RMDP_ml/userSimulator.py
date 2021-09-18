import logging
import math
import os
import random
from concurrent.futures import ThreadPoolExecutor

from Database_Operator.Mongo_Operator import Mongo_Operate
from Math import Geometry


# from Math import Geometry


class userSimulator:

    def __init__(self):
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
        self.DBclient = Mongo_Operate()
        self.p = math.pi / 180

    def generateThread(self):
        cityList = self.DBclient.getAllCity()
        totalCurrentWorker = 2
        logging.info("start generating")
        with ThreadPoolExecutor(max_workers=totalCurrentWorker) as executor:
            for i in range(len(cityList)):
                executor.submit(self.generateOrder, cityList[i], )

    def generateOrder(self, currentCity):
        try:
            generatedLocation = Geometry.randomLocation(currentCity[0]['Longitude'], currentCity[0]['Latitude'],
                                                        currentCity[0]['radius'])

            filteredRestaurantId = self.DBclient.getRestaurantIDBaseOnCity(currentCity[0]['City'])
            self.DBclient.generatingOrder(generatedLocation[1], generatedLocation[0],
                                          filteredRestaurantId[random.randint(0, len(filteredRestaurantId) - 1)][
                                              'Restaurant_ID'])
        except Exception as e:
            logging.critical(e, exc_info=True)
