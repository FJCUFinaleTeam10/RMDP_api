import json
import logging
import os
from datetime import datetime
from schema import Schema, And, Use, Optional, SchemaError
import bson
import numba
import pymongo
from pymongoarrow.monkey import patch_all
import pyarrow
from pymongoarrow.api import Schema
from bson import json_util
from pandas import DataFrame
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import numpy as np


class Mongo_Operate:
    def __init__(self):
        patch_all()
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
        self.client = MongoClient(self.getMongoClientUrl(self.DEBUG))
        self.databaseName = self.client["RMDP"]
        self.restaurantCollection = self.databaseName["restaurant"]
        self.driverCollection = self.databaseName["driver"]
        self.all_citiesCollection = self.databaseName["all_cities"]
        self.country_codeCollection = self.databaseName["country_code"]
        self.orderCollection = self.databaseName["order"]
        self.qlearningCollection = self.databaseName["Q_learning"]
        self.restaurantSchema = ['_id', 'Restaurant_ID', 'Longitude', 'Latitude']
        self.driverSchema = ['_id', 'Capacity', 'City', 'Country_Code', 'Latitude', 'Longitude', 'Velocity',
                             'Driver_ID', 'Reward', 'Route', 'State']

        self.orderSchema = ['driver_id', '_id', 'order_approved_at', 'Latitude', 'Longitude',
                            'Order_ID', 'Qtable_position',
                            'order_delivered_customer_date', 'Qtable_updated', 'order_estimated_delivery_date',
                            'order_request_time',
                            'order_restaurant_carrier_date',
                            'order_restaurant_carrier_restaurantId', 'order_status',
                            ]
        self.citySchema = Schema(
            {
                'Country_Code': pyarrow.int64(),
                'Latitude': pyarrow.float64(),
                'Longitude': pyarrow.float64(),
                'radius': pyarrow.float64()
            })

        self.qlearningSchema = ['_id', 'City', 'action_index', 'capacity', 'center', 'decay_rate', 'episode',
                                'max_epislon', 'min_epislon', 'q_table', 'side_length', 'epsilon', 'nearBY',
                                'state_index', 'gamma',
                                'learning_rate']

    def getMongoClientUrl(self, DEBUG):
        if DEBUG:
            return "mongodb://admin:admin@localhost:27017/RMDP?authSource=admin"
        else:
            return "mongodb://admin:admin@mongodb:27017/RMDP?authSource=admin"

    def getAllCityDataFrame(self):
        data = list(
            map(lambda item: list(map(lambda col: item[col], self.citySchema)), self.all_citiesCollection.find({})))
        return DataFrame(data, columns=self.citySchema)

    def getAllCity(self):
        rawData = self.all_citiesCollection.find_numpy_all({}, schema=self.citySchema)
        data = np.vstack((rawData['Country_Code'], rawData['Latitude'],rawData['Longitude'],rawData['radius'])).T
        return data

    def getDriverBaseOnCityDataFrame(self, cityName):
        data = list(map(lambda item: list(map(lambda col: item[col], self.driverSchema)),
                        self.driverCollection.find({"City": cityName})))
        return DataFrame(data, columns=self.driverSchema)

    def getDriverBaseOnCity(self, cityName):
        return list(self.driverCollection.find({"City": cityName}))

    def getHasOrderDriverBaseOnCityDataFrame(self, cityName):
        data = list(map(lambda item: list(map(lambda col: item[col], self.driverSchema)), self.driverCollection.find({
            '$and': [
                {"City": cityName},
                {"Route": {
                    "$exists": True,
                    "$ne": []
                }
                }
            ]
        })))
        return DataFrame(data, columns=self.driverSchema)

    def getHasOrderDriverBaseOnCity(self, cityName):
        return list(self.driverCollection.find({
            '$and': [
                {"City": cityName},
                {"Route": {
                    "$exists": True,
                    "$ne": []
                }
                }
            ]
        }))

    def getPairedOrderBaseOnCityDataFrame(self, restaurantListID):
        data = list(map(lambda item: list(map(lambda col: item[col], self.orderSchema)), self.orderCollection.find({
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
        })))
        return DataFrame(data, columns=self.orderSchema)

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

    def getPairedOrderBaseOnOrderIDDataFrame(self, orderID):
        data = list(map(lambda item: list(map(lambda col: item[col], self.orderSchema)), self.orderCollection.find({
            "Order_ID": str(orderID)
        })))
        return DataFrame(data, columns=self.orderSchema)

    def getPairedOrderBaseOnOrderID(self, orderID):
        return list(self.orderCollection.find({
            "Order_ID": str(orderID)
        }))

    def getRestaurantIDBaseOnCityData(self, cityName):
        return list(self.restaurantCollection.find({
            "City": cityName
        },
            {
                "Restaurant_ID": 1
            }, ))

    def getRestaurantListBaseOnCityDataFrame(self, cityName):
        data = list(
            map(lambda item: list(map(lambda col: item[col], self.restaurantSchema)), self.restaurantCollection.find({
                "City": cityName
            },
                {"Restaurant_ID": 1,
                 "Longitude": 1,
                 "Latitude": 1
                 })))
        return DataFrame(data, columns=self.restaurantSchema)

    def getRestaurantListBaseOnCity(self, cityName):
        return list(self.restaurantCollection.find({
            "City": cityName
        },
            {"Restaurant_ID": 1,
             "Longitude": 1,
             "Latitude": 1
             }))

    def getOrderBaseOnCityDataFrame(self, filterrestTaurantCode, orderStatus):
        data = list(
            map(lambda item: list(map(lambda col: item[col], self.orderSchema)),
                self.orderCollection.find({"$and": [{"order_status": orderStatus},
                                                    {"order_restaurant_carrier_restaurantId": {
                                                        "$in": filterrestTaurantCode
                                                    }
                                                    }
                                                    ]
                                           })))
        return DataFrame(data, columns=self.orderSchema)

    def getOrderBaseOnCity(self, filterrestTaurantCode, orderStatus):
        return list(
            self.orderCollection.find({"$and": [{"order_status": orderStatus},
                                                {"order_restaurant_carrier_restaurantId": {
                                                    "$in": filterrestTaurantCode
                                                }
                                                }
                                                ]
                                       }))

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

    def insertOrder(self, order):
        try:
            self.orderCollection.insert(
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

    def getRestaurantOrderCount(self, restaurantId):
        return self.restaurantCollection.find({
            "Restaurant_ID": str(restaurantId)
        },
            {
                "order_num": 1
            }, )
