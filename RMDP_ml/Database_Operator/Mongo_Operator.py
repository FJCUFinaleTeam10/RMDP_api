import json
import logging
import os

import numpy as np
import pyarrow
from bson import json_util
from pandas import DataFrame
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongoarrow.api import Schema
from pymongoarrow.monkey import patch_all

patch_all()


def getMongoClientUrl(DEBUG):
    if DEBUG:
        return "mongodb://admin:admin@localhost:27017/RMDP?authSource=admin"
    else:
        return "mongodb://admin:admin@mongodb:27017/RMDP?authSource=admin"


DEBUG = False if int(os.environ['DEBUG']) == 1 else True
client = MongoClient(getMongoClientUrl(DEBUG))
databaseName = client["RMDP"]
restaurantCollection = databaseName["restaurant"]
driverCollection = databaseName["driver"]
all_citiesCollection = databaseName["all_cities"]
country_codeCollection = databaseName["country_code"]
orderCollection = databaseName["order"]
qlearningCollection = databaseName["Q_learning"]

driverPandasSchema = ['_id', 'Capacity', 'City', 'Country_Code', 'Latitude', 'Longitude', 'Velocity',
                'Driver_ID', 'Reward', 'Route', 'State']

orderSchema = Schema({'driver_id': pyarrow.int64(),
                      'order_approved_at': pyarrow.timestamp('ms'),
                      'Latitude': pyarrow.float64(),
                      'Longitude': pyarrow.float64(),
                      'Order_ID': pyarrow.int64(),
                      'Qtable_position': pyarrow.int64(),
                      'order_delivered_customer_date': pyarrow.timestamp('ms'),
                      'Qtable_updated': pyarrow.int64(),
                      'order_estimated_delivery_date':  pyarrow.timestamp('ms'),
                      'order_request_time': pyarrow.timestamp('ms'),
                      'order_restaurant_carrier_date':  pyarrow.timestamp('ms'),
                      'order_restaurant_carrier_restaurantId': pyarrow.int64(),
                      'order_status': pyarrow.int64(),
                      })
citySchema = Schema(
    {
        'Country_Code': pyarrow.int64(),
        'Latitude': pyarrow.float64(),
        'Longitude': pyarrow.float64(),
        'radius': pyarrow.float64(),
        'City_id': pyarrow.int64()
    })
restaurantSchema = Schema({'Restaurant_ID': pyarrow.int64(),
                           'Longitude': pyarrow.float64(),
                           'Latitude': pyarrow.float64(),
                           'order_num': pyarrow.int64()
                           })

qlearningSchema = ['_id', 'City', 'action_index', 'capacity', 'center', 'decay_rate', 'episode',
                   'max_epislon', 'min_epislon', 'q_table', 'side_length', 'epsilon', 'nearBY',
                   'state_index', 'gamma',
                   'learning_rate']


def getAllCity():
    rawData = all_citiesCollection.find_numpy_all({}, schema=citySchema)
    return np.vstack(
        (rawData['City_id'], rawData['Country_Code'], rawData['Latitude'], rawData['Longitude'], rawData['radius'])).T


def getDriverBaseOnCity(cityId):
    rawData = driverCollection.find_numpy_all({'City_id': int(cityId)}, schema=citySchema)
    return np.vstack((rawData['Country_Code'],
                      rawData['Latitude'],
                      rawData['Longitude'],
                      rawData['radius'],
                      rawData['City_id'])).T


def getHasOrderDriverBaseOnCity(cityId):
    rawData = driverCollection.find_numpy_all({
        '$and': [
            {"Driver_ID": int(cityId)},
            {"Route": {
                "$exists": True,
                "$ne": []
            }
            }
        ]
    }, schema=driverSchema)
    return np.vstack((rawData['Country_Code'],
                      rawData['Latitude'],
                      rawData['Longitude'],
                      rawData['radius'],
                      rawData['City_id'])).T


def getPairedOrderBaseOnCity(self, restaurantListID):
    return list(self.orderCollection.find({
        '$and': [
            {"order_restaurant_carrier_restaurantId": {
                "$in": restaurantListID,
            }
            },
            {"order_status": {
                "$in": ["headToRes", "headToCus"]
            }
            }
        ]
    }))


def getPairedOrderBaseOnOrderID(self, orderID):
    return list(self.orderCollection.find({
        "Order_ID": str(orderID)
    }))


def getRestaurantIDBaseOnCityId(cityId):
    rawData = restaurantCollection.find_numpy_all({'City_id': int(cityId)}, schema=restaurantSchema)
    return rawData['Restaurant_ID']


def getRestaurantListBaseOnCity(cityId):
    rawData = restaurantCollection.find_numpy_all({'City_id': int(cityId)}, schema=restaurantSchema)
    return np.vstack((rawData['Restaurant_ID'], rawData['Longitude'], rawData['Latitude'])).T


def getOrderBaseOnCity(filterrestTaurantCode, orderStatus):

    rawData = restaurantCollection.aggregate_numpy_all([{'$match': {"order_status": int(orderStatus),
                                                                    "order_restaurant_carrier_restaurantId": {
                                                                        "$in": filterrestTaurantCode}
                                                                    }}], schema=orderSchema)
    # return np.vstack((rawData['driver_id'], rawData['order_approved_at'], rawData['Latitude'], rawData['Longitude'],
    #                   rawData['Order_ID'], rawData['Qtable_position'], rawData['order_delivered_customer_date'],
    #                   rawData['Qtable_updated'], rawData['order_estimated_delivery_date'], rawData['order_request_time'],
    #                   rawData['order_restaurant_carrier_date'], rawData['order_restaurant_carrier_restaurantId'],
    #                   rawData['order_status'])).T
    return rawData


def updateDriver(self, driver):
    self.driverCollection.update_one({
        'Driver_ID': driver['Driver_ID']
    }, {
        "$set": {
            'Capacity': driver['Capacity'],
            'Velocity': driver['Velocity'],
            'Route': [json.loads(json_util.dumps(index)) for index in driver['Route']],
            'Latitude': driver['Latitude'],
            'Longitude': driver['Longitude'],
            'State': driver['State'],
            'Reward': driver['Reward'],
        },
    })


def updateOrder(self, order):
    try:
        self.orderCollection.update_one({
            '_id': order['_id']
        }, {
            '$set': {
                'order_approved_at': order['order_approved_at'] if 'order_approved_at' in order else None,
                'Longitude': order['Longitude'],
                'Latitude': order['Latitude'],
                'order_delivered_customer_date': order[
                    'order_delivered_customer_date'] if 'order_delivered_customer_date' in order else None,
                'order_request_time': order['order_request_time'],
                'order_restaurant_carrier_date': order[
                    'order_restaurant_carrier_date'] if 'order_restaurant_carrier_date' in order else None,
                'order_restaurant_carrier_restaurantId': order['order_restaurant_carrier_restaurantId'],
                'driver_id': order['driver_id'] if 'driver_id' in order else None,
                'order_status': order['order_status'],
                'Order_ID': order['Order_ID'],
                'order_estimated_delivery_date': order[
                    'order_estimated_delivery_date'] if 'order_estimated_delivery_date' in order else None,
                'Qtable_position': order['Qtable_position'],
                'Qtable_updated': order['Qtable_updated']
            }
        }, upsert=False)
    except PyMongoError as py_mongo_error:
        logging.critical(py_mongo_error, exc_info=True)
    except Exception as e:
        logging.critical(e, exc_info=True)


def insertOrder(order):
    try:
        orderCollection.insert(
            {
                'order_approved_at': order['order_approved_at'] if 'order_approved_at' in order else None,
                'Longitude': order['Longitude'],
                'Latitude': order['Latitude'],
                'order_delivered_customer_date': order[
                    'order_delivered_customer_date'] if 'order_delivered_customer_date' in order else None,
                'order_request_time': order['order_request_time'],
                'order_restaurant_carrier_date': order[
                    'order_restaurant_carrier_date'] if 'order_restaurant_carrier_date' in order else None,
                'order_restaurant_carrier_restaurantId': order['order_restaurant_carrier_restaurantId'],
                'driver_id': order['driver_id'] if 'driver_id' in order else None,
                'order_status': order['order_status'],
                'Order_ID': order['Order_ID'],
                'order_estimated_delivery_date': order[
                    'order_estimated_delivery_date'] if 'order_estimated_delivery_date' in order else None,
                'Qtable_position': order['Qtable_position'],
                'Qtable_updated': order['Qtable_updated']
            }
        )
    except PyMongoError as py_mongo_error:
        logging.critical(py_mongo_error, exc_info=True)


def getQlearning(self, cityName):
    data = list(map(lambda item: list(map(lambda col: item[col], self.qlearningSchema)),
                    self.qlearningCollection.find({"City": cityName})))
    return DataFrame(data, columns=self.qlearningSchema)


def updateQlearning(self, q_setting):
    try:
        self.qlearningCollection.update_one({
            'City': q_setting['City']
        }, {
            '$set': {
                'state_index': q_setting['state_index'],
                'action_index': q_setting['action_index'],
                'q_table': q_setting['q_table'],
                'center': q_setting['center'],
                'side_length': q_setting['side_length'],
                'learning_rate': q_setting['learning_rate'],
                'gamma': q_setting['gamma'],
                'epsilon': q_setting['epsilon'],
                'max_epislon': q_setting['max_epislon'],
                'min_epislon': q_setting['min_epislon'],
                'decay_rate': q_setting['decay_rate'],
                'nearBY': q_setting['nearBY'],
                'capacity': q_setting['capacity'],
                'episode': q_setting['episode']
            }
        }, upsert=False)
    except PyMongoError as py_mongo_error:
        logging.critical(py_mongo_error, exc_info=True)
    except Exception as e:
        logging.critical(e, exc_info=True)


def getRestaurantOrderCount(restaurantId):
    rawData = restaurantCollection.find_numpy_all({'Restaurant_ID': int(restaurantId)}, schema=restaurantSchema)
    return rawData['order_num'][0]
    # return rawData['Restaurant_ID']
