import copy
# from generatingData import generateTestData
# from Math.Geometry import interSectionCircleAndLine
import os
from datetime import datetime, timedelta
from functools import reduce

from pymongo import MongoClient
import itertools
import math
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from operator import attrgetter


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


def mongoClientUrl(DEBUG):
    if DEBUG:
        return "mongodb://admin:admin@localhost:27017/RMDP?authSource=admin"
    else:
        return "mongodb://admin:admin@mongodb:27017/RMDP?authSource=admin"


class RMDP:
    _instance = None

    def __init__(self):
        # self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
        self.DEBUG = True
        # print(int(os.environ['DEBUG']) == 1)
        self.Order_num = 2
        self.Delta_S = 0
        self.time_buffer = 0
        self.t_Pmax = 40
        self.t_ba = 10
        self.delay = 5
        self.maxLengthPost = 5
        self.maxTimePost = 15 * 60
        self.capacity = 5
        self.velocity: float = 50 * 0.2777777777777778
        self.restaurantPrepareTime = 20 * 60
        self.deadlineTime = 40 * 60
        self.Theta_x = []
        self.P_x = []
        self.client = MongoClient(mongoClientUrl(self.DEBUG))
        self.databaseName = self.client["RMDP"]
        self.restaurantCollection = self.databaseName["restaurant"]
        self.driverCollection = self.databaseName["driver"]
        self.all_citiesCollection = self.databaseName["all_cities"]
        self.country_codeCollection = self.databaseName["country_code"]
        self.orderCollection = self.databaseName["order"]

    def generateThread(self):
        cityList = list(self.all_citiesCollection.find())
        totalCurrentWorker = 2
        logging.info("start generating")
        with ThreadPoolExecutor(max_workers=totalCurrentWorker) as executor:
            threads = []
            for i in range(len(cityList)):
                threads.append(executor.submit(self.runRMDP, index=i, cityName=(cityList[i]['City'])))

    def runRMDP(self, index, cityName):
        try:
            print("currentThread:", index)
            restaurantList = list(self.restaurantCollection.find({"City": cityName}))
            driverList = list(self.driverCollection.find({"City": cityName}))
            filterrestTaurantCode = list(map(lambda x: int(x['Restaurant_ID']), restaurantList))
            unAssignOrder = list(self.orderCollection.find({"$and": [{"order_status": "unasgined"}, {
                "order_restaurant_carrier_restaurantId": {"$in": filterrestTaurantCode}}]}))
            postponedOrder = list(self.orderCollection.find({"$and": [{"order_status": "watting"},
                                                                      {"order_restaurant_carrier_restaurantId": {
                                                                          "$in": filterrestTaurantCode}}]
                                                             }))
            if self.maxLengthPost <= len(unAssignOrder):
                self.maxLengthPost = len(unAssignOrder) + 1
                logging.info("upgrade maxLengPostTo:", len(unAssignOrder) + 1)
            delay: float = float("inf")
            slack = 0

            for permutation in itertools.permutations(unAssignOrder):

                currentDriverList = copy.deepcopy(driverList)
                P_hat = copy.deepcopy(postponedOrder)

                for D in permutation:
                    currentPairdRestaurent = next(
                        filter(lambda x: int(x['Restaurant_ID']) == int(D["order_restaurant_carrier_restaurantId"]),
                               restaurantList), None)
                    currentPairdDriverId = self.FindVehicle(D, currentPairdRestaurent, currentDriverList)
                    D["driver_id"] = (str(currentDriverList[currentPairdDriverId]['_id']))
                    currentPairdRestaurent['orderId'] = str(D['_id'])
                    currentDriverList[currentPairdDriverId]['Capacity'] += 1
                    currentDriverList[currentPairdDriverId]['Route'] = copy.deepcopy(
                        self.AssignOrder(D, currentDriverList[currentPairdDriverId], currentPairdRestaurent))
                    if self.Postponement(P_hat, D, self.maxLengthPost, self.t_Pmax):
                        P_hat.append(D)
                    else:
                        while (datetime.strptime(D['order_request_time'], '%d-%m-%Y %H:%M:%S') - datetime.strptime(
                                P_hat[0]['order_request_time'], '%d-%m-%Y %H:%M:%S')) >= timedelta(minutes=self.t_Pmax):

                            PairdDriverId = self.FindVehicle(P_hat[0])
                            P_hat[0]['driver_id'] = str(currentDriverList[PairdDriverId]['_id'])
                            driverList[PairdDriverId]['Capacity'] += 1
                            PairedRestaurent = copy.deepcopy(next(filter(lambda x: int(x['Restaurant_ID']) == int(
                                pospondedOrder["order_restaurant_carrier_restaurantId"]), restaurantList), None))
                            PairedRestaurent['orderId'] = str(P_hat[0]['_id'])
                            driverList[PairdDriverId]['Route'] = copy.deepcopy(
                                self.AssignOrder(P_hat[0], currentDriverList[PairdDriverId], PairedRestaurent))
                            P_hat.pop(0)
                            if len(P_hat) == 0:
                                break
                        if len(P_hat) >= self.maxLengthPost:
                            for pospondedOrder in P_hat:
                                PairedRestaurent = copy.deepcopy(next(filter(lambda x: int(x['Restaurant_ID']) == int(
                                    pospondedOrder["order_restaurant_carrier_restaurantId"]), restaurantList), None))
                                PairdDriverId = self.FindVehicle(pospondedOrder, PairedRestaurent, currentDriverList)
                                driverList[PairdDriverId]['Capacity'] += 1
                                pospondedOrder['driver_id'] = driverList[PairdDriverId]['_id']
                                PairedRestaurent['orderId'] = (pospondedOrder['_id'])
                                currentDriverList[PairdDriverId]['Route'] = copy.deepcopy(
                                    self.AssignOrder(pospondedOrder, currentDriverList[PairdDriverId],
                                                     PairedRestaurent))
                            P_hat.clear()
                        P_hat.append(D)
                S = self.TotalDelay(driverList)
                currentSlack = self.Slack(driverList)
                if (S < delay) or ((S == delay) and (currentSlack < slack)):
                    slack = currentSlack
                    delay = S
                    driverList = copy.deepcopy(currentDriverList)
                    postponedOrder = copy.deepcopy(P_hat)
            self.Remove()
            self.updateValue()
            print("Thread:", index, " is finished")
        except Exception as e:
            logging.critical(e, exc_info=True)

    def deltaSDelay(self, driver):
        try:
            delay: float = 0.0
            tripTime: float = 0.0
            currentDriverLocation = {'Longitude': driver['Longitude'], 'Latitude': driver['Latitude']}
            currentDriver = copy.deepcopy(driver)
            currentDriver['Route'].insert(0, currentDriverLocation)
            for i in range(1, len(currentDriver['Route']), 1):
                previousNode = currentDriver['Route'][i - 1]
                currentNode = currentDriver['Route'][i]
                currentDistance = self.distance(float(previousNode['Latitude']), float(previousNode['Longitude']),
                                                float(currentNode['Latitude']), float(currentNode['Longitude']))
                tripTime += currentDistance / self.velocity
                if 'order_request_time' in currentNode:
                    deadlineTime = timedelta(seconds=self.deadlineTime)
                    timeComplete = timedelta(seconds=tripTime) + timedelta(
                        minutes=self.time_buffer) + datetime.now() + timedelta(hours=8)
                    timeDeadline = datetime.strptime(currentNode['order_request_time'],
                                                     "%d-%m-%Y %H:%M:%S") + deadlineTime
                    timeDelay = timeComplete - timeDeadline
                    delay += timeDelay.total_seconds()
            return max(0, delay)
        except Exception as e:
            logging.critical(e, exc_info=True)

    def AssignOrder(self, order, pairedDriver, currentParedRestaurent):
        try:
            if not pairedDriver['Route']:
                pairedDriver['Route'].append(currentParedRestaurent)
                pairedDriver['Route'].append(order)
            else:
                first: int = 0
                second: int = 1
                minDelayTime = float('inf')
                for i in range(0, len(pairedDriver['Route']), 1):  # control Restaurant
                    for j in range(i + 1, len(pairedDriver['Route']) + 2,
                                   1):  # find all the possible positioins of new order

                        tmpDriver = copy.deepcopy(pairedDriver)
                        tmpDriver['Route'].insert(i, currentParedRestaurent)
                        tmpDriver['Route'].insert(j, order)
                        delayTime = self.deltaSDelay(tmpDriver)

                        if minDelayTime > delayTime:
                            minDelayTime = delayTime
                            first = i
                            second = j

                pairedDriver['Route'].insert(first, currentParedRestaurent)
                pairedDriver['Route'].insert(second, order)
            return pairedDriver['Route']
        except Exception as e:
            logging.critical(e, exc_info=True)

    # main function

    def Slack(self, Theta_hat):
        return reduce(lambda x, y: self.slackDelay(x) + self.slackDelay(y), Theta_hat, 0.0)

    def tripTime(self, driv, res, order):
        try:
            disDriver2Res = self.distance(float(driv['Latitude']), float(driv['Longitude']), float(res['Latitude']),
                                          float(res['Longitude']))
            Res2Delivery = self.distance(float(res['Latitude']), float(res['Longitude']),
                                         float(order['Latitude']),
                                         float(order['Longitude']))
            return float(disDriver2Res + Res2Delivery / float(self.velocity))
        except Exception as e:
            logging.critical(e, exc_info=True)

    def FindVehicle(self, Order, OrderRestaurant, driverList):
        try:
            handleDriver = list(filter(lambda driver: int(driver['Capacity']) < int(self.capacity), driverList))
            distanceList = list(map(lambda x: self.tripTime(x, OrderRestaurant, Order), handleDriver))
            minDriver = distanceList.index(min(distanceList))
            return minDriver
        except Exception as e:
            logging.critical(e, exc_info=True)

    def slackDelay(self, driver):
        try:
            delay: int = 0
            tripTime: int = 0
            currentRoute: list = copy.deepcopy(driver['Route'])
            currentRoute.append(driver)
            for i in range(1, len(currentRoute), 1):
                currentDistance = self.distance(float(currentRoute[i - 1]['Latitude']),
                                                float(currentRoute[i - 1]['Longitude']),
                                                float(currentRoute[i]['Latitude']), float(currentRoute[i]['Longitude']))
                tripTime += currentDistance / self.velocity
                if 'restaurantId' in currentRoute[i]:
                    deadLine = datetime.strptime(currentRoute[i]['deadLineTime'],
                                                 "%d-%m-%Y %H:%M:%S") - datetime.now() + timedelta(hours=8)
                    delayTime = timedelta(seconds=tripTime) - timedelta(seconds=self.time_buffer) - deadLine
                    delay += max(0, delayTime.total_seconds())
            return delay
        except Exception as e:
            logging.critical(e, exc_info=True)

    def TotalDelay(self, theta_Hat):
        try:
            totalSlack: int = 0
            for routePerVehicle in theta_Hat:
                totalSlack += self.deltaSDelay(routePerVehicle)
            return totalSlack
        except Exception as e:
            logging.critical(e, exc_info=True)

    def Remove(self):
        try:
            for pospondedOrder in self.P_x:
                currentPairedDriverList = list(
                    filter(lambda x: str(x.id) == str(pospondedOrder['driverId']), self.Theta_x))
                currentPairedDriver = currentPairedDriverList[0]
                targetRoute: list = next(
                    (driver for driver in self.Theta_x if str(driver.id) == str(currentPairedDriver.id)), [])

                ans = list(filter(lambda x: (('restaurantId' in x) and
                                             str(x['orderId']) != str(pospondedOrder['orderId'])) or (
                                                    ('requestTime' not in x) and ('route' not in x) and str(
                                                x['orderId']) !=
                                                    str(pospondedOrder['orderId'])), targetRoute['route']))
                targetRoute['route'] = copy.deepcopy(ans[:])
        except Exception as e:
            logging.critical(e, exc_info=True)

    def Postponement(self, P_hat, D, p_max, t_Pmax):
        try:
            if len(P_hat) == 0:  # if postponement set is empty
                return True
            elif len(P_hat) < self.maxLengthPost:  # if number of postponement <= max of postponement

                if datetime.strptime(D['order_request_time'], '%d-%m-%Y %H:%M:%S') - datetime.strptime(
                        P_hat[0]['order_request_time'], '%d-%m-%Y %H:%M:%S') < timedelta(minutes=self.t_Pmax):
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            logging.critical(e, exc_info=True)

    def distance(self, lat1, lon1, lat2, lon2):
        try:
            p = math.pi / 180
            a = 0.5 - math.cos((lat2 - lat1) * p) / 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (
                    1 - math.cos((lon2 - lon1) * p)) / 2
            return 12742 * math.asin(math.sqrt(a))  # 2*R*asin...
        except Exception as e:
            logging.critical(e, exc_info=True)

    def updateValue(self):
        try:
            updateDriver = list(filter(lambda x: len(x['Route']) > 0, self.Theta_x))
            for pairdDriver in updateDriver:
                currentObject = pairdDriver.to_mongo().to_dict()
                self.driverCollection.update_one({
                    '_id': pairdDriver.id
                }, {
                    '$set': {
                        'capacity': currentObject['capacity'],
                        'route': currentObject['route'],
                        'velocity': currentObject['velocity'],
                    }
                }, upsert=False)
        except Exception as e:
            logging.critical(e, exc_info=True)

    def updatePosponedOrder(self):
        for postpoendOrder in self.P_x:
            try:
                self.orderCollection.update_one({
                    '_id': postpoendOrder.id
                }, {
                    '$set': {
                        'order_status': 'watting'
                    }
                }, upsert=False)
            except Exception as e:
                logging.critical(e, exc_info=True)

    def updatePairdOrder(self):
        for pairedOrder in self.Theta_x:
            try:
                currentObject = pairedOrder.to_mongo().to_dict()
                self.orderCollection.objects(id=currentObject.id).update(
                    order_status='processing'
                )
            except Exception as e:
                logging.critical(e, exc_info=True)


test = RMDP()
test.generateThread()
