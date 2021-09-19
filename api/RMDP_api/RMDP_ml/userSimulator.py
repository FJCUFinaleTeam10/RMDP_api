import logging
import math
import os
import random
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
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
            generatedLocation = Geometry.randomLocation(currentCity['Longitude'], currentCity['Latitude'],
                                                        currentCity['radius'])
            filteredRestaurantId = self.DBclient.getRestaurantIDBaseOnCity(currentCity['City'])

            self.DBclient.insertOrder({
                'order_approved_at': None,
                'order_delivered_customer_date': None,
                'order_restaurant_carrier_date': None,
                'driver_id': None,
                'order_estimated_delivery_date': None,
                'Longitude': generatedLocation[1],
                'Latitude': generatedLocation[0],
                'order_request_time': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                'order_restaurant_carrier_restaurantId':
                    filteredRestaurantId[random.randint(0, len(filteredRestaurantId) - 1)]['Restaurant_ID'],
                'order_status': 'unassigned',
                'Order_ID': str(uuid.uuid4())
            })
        except Exception as e:
            logging.critical(e, exc_info=True)



