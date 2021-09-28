import logging
import os
import uuid
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import PyMongoError


class Mongo_Operate:
    def __init__(self):
        self.DEBUG = True
        # self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
        self.client = MongoClient(self.getMongoClientUrl(self.DEBUG))
        self.databaseName = self.client["RMDP"]
        self.restaurantCollection = self.databaseName["restaurant"]
        self.driverCollection = self.databaseName["driver"]
        self.all_citiesCollection = self.databaseName["all_cities"]
        self.country_codeCollection = self.databaseName["country_code"]
        self.orderCollection = self.databaseName["order"]

    def getMongoClientUrl(self, DEBUG):
        if DEBUG:
            return "mongodb://admin:admin@localhost:27017/RMDP?authSource=admin"
        else:
            return "mongodb://admin:admin@mongodb:27017/RMDP?authSource=admin"

    def getAllCity(self):
        return list(self.all_citiesCollection.find())

    def getDriverBaseOnCity(self, cityName):
        return list(self.driverCollection.find({"City": cityName}))

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

    def getPairedOrderBaseOnCity(self, restaurantList):
        return list(self.orderCollection.find({
            '$and': [
                {"order_restaurant_carrier_restaurantId": {
                    "$in": restaurantList,
                }
                },
                {"order_status": {
                    "$in": ["headToRes", "headToCus"]
                }
                }
            ]
        }))

    def getRestaurantIDBaseOnCity(self, cityName):
        return list(self.restaurantCollection.find(
            {
                "City": cityName
            },
            {
                "Restaurant_ID": 1
            }
        ))

    def getRestaurantListBaseOnCity(self, cityName):
        return list(self.restaurantCollection.find(
            {
                "City": cityName
            },
            {"Restaurant_ID": 1,
             "Longitude": 1,
             "Latitude": 1
             }
        )
        )

    def getOrderBaseOnCity(self, filterrestTaurantCode, orderStatus):
        try:
            return list(self.orderCollection.find(
                {"$and": [{"order_status": orderStatus},
                          {"order_restaurant_carrier_restaurantId": {
                              "$in": filterrestTaurantCode
                          }
                          }
                          ]
                 }
            )
            )
        except PyMongoError as py_mongo_error:
            logging.critical(py_mongo_error, exc_info=True)

    def updateDriver(self, driver):
        try:
            self.driverCollection.update_one({
                'Driver_ID': driver['Driver_ID']
            }, {
                "$set": {
                    'Capacity': driver['Capacity'],
                    'Velocity': driver['Velocity'],
                    'Route': driver['Route'],
                    'Latitude': driver['Latitude'],
                    'Longitude': driver['Longitude'],
                },
            })
        except PyMongoError as py_mongo_error:
            logging.critical(py_mongo_error, exc_info=True)

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
                }
            }, upsert=False)
        except Exception as e:
            logging.critical(e, exc_info=True)
        except PyMongoError as py_mongo_error:
            logging.critical(py_mongo_error, exc_info=True)

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
                }
            )
        except PyMongoError as py_mongo_error:
            logging.critical(py_mongo_error, exc_info=True)
