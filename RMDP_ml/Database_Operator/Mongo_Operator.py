import json
import logging
import os
from numba import jit
import numpy as np
import pyarrow
from bson import json_util
from pandas import DataFrame
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongoarrow.api import Schema
from pymongoarrow.monkey import patch_all
import time
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
qlearningCollection = databaseName["q_learning"]
RouteCollection = databaseName["route"]
driverPandasSchema = Schema({
    'Driver_ID': pyarrow.int64(),
    'Country_Code': pyarrow.int64(),
    'City_id': pyarrow.int64(),
    'Longitude': pyarrow.float64(),
    'Latitude': pyarrow.float64(),
    'Velocity': pyarrow.int64(),
    'Capacity': pyarrow.int64(),
    'State': pyarrow.int64(),
    'Reward': pyarrow.int64(),
    'Node_ID': pyarrow.int64(),
    'Node_num': pyarrow.int64()
})
routeSchema = Schema({'Driver_ID':pyarrow.int64()
                     ,'Latitude' :pyarrow.float64()
                     ,'Longitude':pyarrow.float64()
                     ,'nodetype':pyarrow.int64()
                     ,'Restaurant_ID':pyarrow.int64(),
                      'Order_ID':pyarrow.int64(),
                      'Node_ID':pyarrow.int64()
                         ,'delivered':pyarrow.int64()
                      })
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

qlearningSchema = ['City_id','state_index', 'action_index','q_table',  'center',
                     'side_length',
                   'learning_rate',
                    'gamma',
                   'epsilon','max_epislon', 'min_epislon', 'decay_rate',  'nearBY', 'episode','capacity']


def getAllCity():
    rawData = all_citiesCollection.find_numpy_all({}, schema=citySchema)
    return np.vstack(
        (rawData['City_id'], rawData['Country_Code'], rawData['Latitude'], rawData['Longitude'], rawData['radius'])).T


def getDriverBaseOnCity(cityId):
    rawData = driverCollection.find_numpy_all({'City_id': int(cityId)}, schema=driverPandasSchema)

    return np.vstack((rawData['Driver_ID'],rawData['Country_Code'],
    rawData['City_id'] ,rawData['Longitude'],
    rawData['Latitude'],rawData['Velocity'],rawData['Capacity'],rawData['State'],
    rawData['Reward'],rawData['Node_ID'],rawData['Node_num'])).T


def getHasOrderDriverBaseOnCity(cityId):
    rawData = driverCollection.aggregate_numpy_all(
        [{'$match': {"City_id": int(cityId),
                     "Capacity": {"$gt": 0}
                     }}], schema=driverPandasSchema)

    return np.vstack((rawData['Driver_ID'], rawData['Country_Code'],
               rawData['City_id'], rawData['Longitude'],
               rawData['Latitude'], rawData['Velocity'], rawData['Capacity'], rawData['State'],
               rawData['Reward'], rawData['Node_ID'], rawData['Node_num'])).T



def getPairedOrderBaseOnCity( restaurantListID):
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


def getPairedOrderBaseOnOrderID(orderID):
    rawData =  orderCollection.find_numpy_all({'Order_ID': int(orderID)}, schema=orderSchema)
    rawData = np.asmatrix((
        rawData['driver_id'],
        rawData['order_approved_at'],
        rawData['Latitude'],
        rawData['Longitude'],
        rawData['Order_ID'],
        rawData['Qtable_position'],
        rawData['order_delivered_customer_date'],
        rawData['Qtable_updated'],
        rawData['order_estimated_delivery_date'],
        rawData['order_request_time'],
        rawData['order_restaurant_carrier_date'],
        rawData['order_restaurant_carrier_restaurantId'],
        rawData['order_status']
    )).T

    rawData = np.asarray(rawData)

    return rawData

def getRestaurantIDBaseOnCityId(cityId):
    rawData = restaurantCollection.find_numpy_all({'City_id': int(cityId)}, schema=restaurantSchema)
    return rawData['Restaurant_ID']


def getRestaurantListBaseOnCity(cityId):
    rawData = restaurantCollection.find_numpy_all({'City_id': int(cityId)}, schema=restaurantSchema)
    return np.vstack((rawData['Restaurant_ID'], rawData['Longitude'], rawData['Latitude'], rawData['order_num'])).T



def getDriverRouteBaseOnDriverID(driverId):
    rawData =RouteCollection.find_numpy_all({'Driver_ID': int(driverId),'delivered':0}, schema=routeSchema)
    if len(rawData)==0:
        return np.zeros(shape=(0,8))
    else:
        return np.vstack((
            rawData['Driver_ID']
            , rawData['Latitude']
        , rawData['Longitude']
        , rawData['nodetype']
        , rawData['Restaurant_ID'],
        rawData['Order_ID'],
        rawData['Node_ID']
        , rawData['delivered']
        )).T







def getOrderBaseOnCity(filterrestTaurantCode, orderStatus):

    rawData = orderCollection.aggregate_numpy_all([{'$match': {"order_status": int(orderStatus),
                                                                    "order_restaurant_carrier_restaurantId": {
                                                                        "$in": filterrestTaurantCode}
                                                                    }}], schema=orderSchema)
    rawData = np.asmatrix((
        rawData['driver_id'],
        rawData['order_approved_at'],
        rawData['Latitude'],
        rawData['Longitude'],
        rawData['Order_ID'],
        rawData['Qtable_position'],
        rawData['order_delivered_customer_date'],
        rawData['Qtable_updated'],
        rawData['order_estimated_delivery_date'],
        rawData['order_request_time'],
        rawData['order_restaurant_carrier_date'],
        rawData['order_restaurant_carrier_restaurantId'],
        rawData['order_status']
                           )).T

    rawData = np.asarray(rawData)
    return rawData



def updateRoute(Route):
    Route = Route.reshape(1,8)
    RouteCollection.update_one(
        {
            'Driver_ID':Route[0][0],
            'Resrtaurant_ID':Route[0][4],
            'Order_ID':Route[0][5],
            'nodetype':Route[0][3]
        },{
            "$set":{
                'Driver_ID': Route[0][0]
                , 'Latitude': Route[0][1]
                , 'Longitude': Route[0][2]
                , 'nodetype': Route[0][3]
                , 'Restaurant_ID': Route[0][4],
                'Order_ID': Route[0][5],
                'Node_ID': Route[0][6]
                , 'delivered': Route[0][7]
            }
        }, upsert=True
    )

def updateDriver(driver):
    driverCollection.update_one({
        'Driver_ID': driver[0]
    }, {
        "$set": {
            'Capacity': driver[6],
            'Velocity': driver[5],
            'Latitude': driver[4],
            'Longitude': driver[3],
            'State': driver[7],
            'Reward': driver[8],
        },
    })

def updateRestaurantOrdernum(restaurantID,currentordernum):
    try:
        restaurantCollection.update_one({
            'Restaurant_ID':int(restaurantID)
        },{
            '$set': {
                'order_num':int(currentordernum)
            }
        }, upsert=False)
    except PyMongoError as py_mongo_error:
        logging.critical(py_mongo_error, exc_info=True)
    except Exception as e:
        logging.critical(e, exc_info=True)
def updateOrder(order):
    try:
        orderCollection.update_one({
            'Order_ID': order[4],
            'order_restaurant_carrier_restaurantId':order[11]
        }, {
            '$set': {

                'driver_id': None if np.isnan(order[0])else order[0],
                'order_approved_at': order[1],
                'Latitude': order[2],
                'Longitude': order[3],
                'Order_ID': order[4],
                'Qtable_position': order[5],
                'order_delivered_customer_date': order[6],
                'Qtable_updated': order[7],
                'order_estimated_delivery_date': order[8],
                'order_request_time': order[9],
                'order_restaurant_carrier_date': order[10],
                'order_restaurant_carrier_restaurantId': order[11],
                'order_status': order[12],
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
                'order_approved_at': order['order_approved_at'] ,
                'Longitude': order['Longitude'],
                'Latitude': order['Latitude'],
                'order_delivered_customer_date': order[
                    'order_delivered_customer_date'],
                'order_request_time': order['order_request_time'],
                'order_restaurant_carrier_date': order[
                    'order_restaurant_carrier_date'],
                'order_restaurant_carrier_restaurantId': order['order_restaurant_carrier_restaurantId'],
                'driver_id': order['driver_id'],
                'order_status': order['order_status'],
                'Order_ID': order['Order_ID'],
                'order_estimated_delivery_date': order['order_estimated_delivery_date'],
                'Qtable_position': order['Qtable_position'],
                'Qtable_updated': order['Qtable_updated']
            }
        )
    except PyMongoError as py_mongo_error:
        logging.critical(py_mongo_error, exc_info=True)


    except PyMongoError as py_mongo_error:
        logging.critical(py_mongo_error, exc_info=True)
def getQlearning(cityName):
    data = list(map(lambda item: list(map(lambda col: item[col], qlearningSchema)),
                    qlearningCollection.find({"City_id": cityName})))
    return DataFrame(data, columns=qlearningSchema).to_numpy()






def updateQlearning(q_setting):
    try:
        qlearningCollection.update_one({
            'City_id': q_setting[0][0]
        }, {
            '$set': {
                'state_index': q_setting[0][1],
                'action_index': q_setting[0][2],
                'q_table': q_setting[0][3],
                'center': q_setting[0][4],
                'side_length': q_setting[0][5],
                'learning_rate': q_setting[0][6],
                'gamma': q_setting[0][7],
                'epsilon': q_setting[0][8],
                'max_epislon': q_setting[0][9],
                'min_epislon': q_setting[0][10],
                'decay_rate': q_setting[0][11],
                'nearBY': q_setting[0][12],
                'capacity': q_setting[0][14],
                'episode': q_setting[0][13]
            }
        }, upsert=False)
    except PyMongoError as py_mongo_error:
        logging.critical(py_mongo_error, exc_info=True)
    except Exception as e:
        logging.critical(e, exc_info=True)


def getRestaurantOrderCount(restaurantId):
    rawData = restaurantCollection.find_numpy_all({'Restaurant_ID': int(restaurantId)}, schema=restaurantSchema)
    return rawData['order_num'][0] #accumulate order or current order
    # return rawData['Restaurant_ID']
def lengthOforder():
    return orderCollection.count()