import logging
import os
from datetime import datetime, timedelta
import uuid

from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError


class Mongo_Operate:
    def __init__(self):
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
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

    def updateOrderToRes(self, order_id):
        try:
            self.orderCollection.update_one(
                {
                    'Order_ID': order_id
                },
                {
                    "$set": {
                        "order_restaurant_carrier_date": datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                        "order_status": "headToCus"
                    }
                }
            )
        except Exception as e:
            logging.critical(e, exc_info=True)
        except PyMongoError as py_mongo_error:
            logging.critical(py_mongo_error, exc_info=True)

    def updateOrderToCus(self, order_id):
        try:
            self.orderCollection.update_one(
                {
                    'Order_ID': order_id
                },
                {
                    "$set": {
                        "order_delivered_customer_date": datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                        "order_status": "delivered"
                    }

                }
            )
        except Exception as e:
            logging.critical(e, exc_info=True)
        except PyMongoError as py_mongo_error:
            logging.critical(py_mongo_error, exc_info=True)

        except Exception as e:
            logging.critical(e, exc_info=True)

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

    def updateDriver(self, driver,Velocity):
        try:
            self.driverCollection.update_one({
                'Driver_ID': driver['Driver_ID']
            }, {
                "$set": {
                    'Capacity': driver['Capacity'],
                    'Velocity': Velocity,
                    'Route': driver['Route'],
                },
                "$currentDate": {
                    "lastModified": True
                }
            })
        except PyMongoError as py_mongo_error:
            logging.critical(py_mongo_error, exc_info=True)

    def updatePairdOrder(self, order):
        try:
            self.orderCollection.update_one({
                '_id': order['_id']
            }, {
                '$set': {
                    'order_approved_at': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                    'order_status': 'headToRes',
                    'driver_id': order['driver_id']
                }
            }, upsert=False)
        except PyMongoError as py_mongo_error:
            logging.critical(py_mongo_error, exc_info=True)

    def updatePosponedOrder(self, order):
        try:
            self.orderCollection.update_one({
                '_id': order['_id']
            }, {
                '$set': {
                    'order_status': 'watting'
                }
            }, upsert=False)
        except Exception as e:
            logging.critical(e, exc_info=True)
        except PyMongoError as py_mongo_error:
            logging.critical(py_mongo_error, exc_info=True)

    def generatingOrder(self, Longitude, Latiude, Id):
        try:
            self.orderCollection.insert(
                {
                    'order_approved_at': None,
                    'Longitude': Longitude,
                    'Latitude': Latiude,
                    'order_delivered_customer_date': None,
                    'order_request_time': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                    'order_restaurant_carrier_date': None,
                    'order_restaurant_carrier_restaurantId': Id,
                    'driver_id': None,
                    'order_status': 'unasgined',
                    'Order_ID': str(uuid.uuid4())
                }
            )
        except PyMongoError as py_mongo_error:
            logging.critical(py_mongo_error, exc_info=True)
