import copy
import logging
import math
import os
import random
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from Database_Operator.Mongo_Operator import Mongo_Operate
from Math import Geometry
import json


# from Math import Geometry


class userSimulator:

    def __init__(self, cityIndex, restaurant_prepareTime, velocity, deadline, capacity, q_table):
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
        self.DBclient = Mongo_Operate()
        self.p = math.pi / 180
        self.time_tik = 0
        with open('output.json') as f:
            data = copy.deepcopy(json.load(f))
        self.order_record = copy.deepcopy(data)
        self.cityList = self.DBclient.getAllCity()  # get all city
        self.cityIndex = cityIndex
        self.driverList = self.DBclient.getDriverBaseOnCity(self.cityList[self.cityIndex]['City'])
        self.orders = []
    def generateThread(self, time_tik, orders, driverList):
        self.time_tik = time_tik
        totalCurrentWorker = 1
        logging.info("start generating")
        with ThreadPoolExecutor(max_workers=totalCurrentWorker) as executor:
            executor.submit(self.generateOrder, self.cityList[self.cityIndex])

    def generateOrder(self, currentCity):
        try:
            '''generatedLocation = Geometry.randomLocation(currentCity['Longitude'], currentCity['Latitude'],
                                                        currentCity['radius'])
            filteredRestaurantId = self.DBclient.getRestaurantIDBaseOnCity(currentCity['City'])
            order_now = {
                "order_approved_at": None,
                "order_delivered_customer_date": None,
                "order_restaurant_carrier_date": None,
                "driver_id": None,
                "order_estimated_delivery_date": None,
                "Longitude": generatedLocation[1],
                "Latitude": generatedLocation[0],
                "order_request_time": self.time_tik,
                "order_restaurant_carrier_restaurantId":
                    filteredRestaurantId[random.randint(0, len(filteredRestaurantId) - 1)]["Restaurant_ID"],
                "order_status": "unassigned",
                "Order_ID": str(uuid.uuid4()),
                "Qtable_position": 0,
                "Qtable_updated":0
            }
            #print(order_now)
            f = open('output.json', 'a')
            t = json.dumps(order_now)
            f.write(t+",")
            f.close'''
            self.DBclient.insertOrder(self.order_record[0])
            self.order_record.pop(0)
        except Exception as e:
            logging.critical(e, exc_info=True)



