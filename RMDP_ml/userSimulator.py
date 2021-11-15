import logging
import math
import random
from collections import OrderedDict
from datetime import datetime

#import numba as nb
import numpy as np
import pyarrow

from RMDP_ml.Database_Operator import Mongo_Operator
from RMDP_ml.Math import Geometry

p = math.pi / 180


def generateThread():
    logging.info("start generating")
    cityList = Mongo_Operator.getAllCity()
    np.apply_along_axis(generateOrder, axis=1, arr=cityList)


def generateOrder(currentCity):
    try:
        # 'City_id','Country_Code','Latitude','Longitude','radius'
        generatedLocation = Geometry.randomLocation(currentCity[3], currentCity[2], currentCity[4])
        restaurant = Mongo_Operator.getRestaurantListBaseOnCity(currentCity[0])
        filteredRestaurantId = Mongo_Operator.getRestaurantIDBaseOnCityId(currentCity[0])
        targetRestaurantId = filteredRestaurantId[random.randint(0, len(filteredRestaurantId) - 1)]
        #currentOrderCount = Mongo_Operator.getRestaurantOrderCount(targetRestaurantId)
        orderLength = Mongo_Operator.lengthOforder()
        order = np.array([])
        Mongo_Operator.insertOrder({
            'order_approved_at': None,
            'order_delivered_customer_date': None,
            'order_restaurant_carrier_date': None,
            'driver_id': 0,
            'order_estimated_delivery_date': None,
            'Longitude': generatedLocation[1],
            'Latitude': generatedLocation[0],
            'order_request_time': datetime.now(),
            'order_restaurant_carrier_restaurantId': float(targetRestaurantId),
            'order_status': 0,
            'Order_ID': orderLength+1,
            'Qtable_position': 0,
            'Qtable_updated': 0,
            'customer_phone_number': None
        })

        #Mongo_Operator.updateRestaurantOrdernum(float(targetRestaurantId),currentOrderCount+1)
    except Exception as e:
        logging.critical(e, exc_info=True)


#   unassigned: 0
#   waiting: 1
#   headToRes: 2
#   head ToCus: 3
#   deliverd: 4

