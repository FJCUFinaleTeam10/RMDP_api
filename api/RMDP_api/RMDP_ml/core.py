import copy
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
import itertools
import math
import logging
from concurrent.futures import ThreadPoolExecutor


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
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
        # self.DEBUG = True
        # print(int(os.environ['DEBUG']) == 1)
        self.Delta_S = 0
        self.time_buffer = timedelta(minutes=0)
        self.t_Pmax = timedelta(minutes=40)
        self.t_ba = 10
        self.delay = 5
        self.maxLengthPost = 5
        self.capacity = 5
        self.velocity: float = 50 * 0.2777777777777778
        self.restaurantPrepareTime = timedelta(minutes=20)
        self.deadlineTime = timedelta(minutes=40)
        self.client = MongoClient(mongoClientUrl(self.DEBUG))
        self.databaseName = self.client["RMDP"]
        self.restaurantCollection = self.databaseName["restaurant"]
        self.driverCollection = self.databaseName["driver"]
        self.all_citiesCollection = self.databaseName["all_cities"]
        self.country_codeCollection = self.databaseName["country_code"]
        self.orderCollection = self.databaseName["order"]
        self.p = math.pi / 180

    def generateThread(self):
        cityList = list(self.all_citiesCollection.find())
        totalCurrentWorker = 2
        logging.info("start generating")
        with ThreadPoolExecutor(max_workers=totalCurrentWorker) as executor:
            threads = []
            for i in range(len(cityList)):
                threads.append(executor.submit(self.runRMDP, index=i, cityName=(cityList[i]['City'])))
        logging.info("tasl completed")

    def runRMDP(self, index, cityName):
        try:
            logging.info(index, "is started")
            delay: float = float("inf")
            slack = 0
            skipPostponement = False
            pairdOrder = []
            restaurantList = list(
                self.restaurantCollection.find({"City": cityName}, {"Restaurant_ID": 1, "Longitude": 1, "Latitude": 1}))
            driverList = list(self.driverCollection.find({"City": cityName}))
            filterrestTaurantCode = list(map(lambda x: int(x['Restaurant_ID']), restaurantList))
            unAssignOrder = list(self.orderCollection.find({"$and": [{"order_status": "unasgined"}, {
                "order_restaurant_carrier_restaurantId": {"$in": filterrestTaurantCode}}]}))
            postponedOrder = list(self.orderCollection.find({"$and": [{"order_status": "watting"},
                                                                      {"order_restaurant_carrier_restaurantId": {
                                                                          "$in": filterrestTaurantCode}}]
                                                             }))

            for order in unAssignOrder: order['order_request_time'] = datetime.strptime(order['order_request_time'],
                                                                                        '%d-%m-%Y %H:%M:%S')
            for order in postponedOrder: order['order_request_time'] = datetime.strptime(order['order_request_time'],
                                                                                         '%d-%m-%Y %H:%M:%S')

            if len(unAssignOrder) == 0 and len(postponedOrder) > 0:
                skipPostponement = True
                unAssignOrder = copy.deepcopy(postponedOrder)
                postponedOrder.clear()
            if self.maxLengthPost <= len(unAssignOrder):
                self.maxLengthPost = len(unAssignOrder) + 1
                logging.info("upgrade maxLengPostTo:", len(unAssignOrder) + 1)

            for permutation in itertools.permutations(unAssignOrder):

                currentDriverList = copy.deepcopy(driverList)
                P_hat = copy.deepcopy(postponedOrder)
                currentPairdOrder = copy.deepcopy(pairdOrder)
                for D in permutation:
                    currentPairdRestaurent = next(
                        filter(lambda x: int(x['Restaurant_ID']) == int(D["order_restaurant_carrier_restaurantId"]),
                               restaurantList), None)
                    currentPairdDriverId = self.FindVehicle(D, currentPairdRestaurent, currentDriverList)
                    D["driver_id"] = str(currentDriverList[currentPairdDriverId]['Driver_ID'])
                    currentDriverList[currentPairdDriverId]['Capacity'] += 1
                    currentDriverList[currentPairdDriverId]['Route'] = copy.deepcopy(
                        self.AssignOrder(D, currentDriverList[currentPairdDriverId], currentPairdRestaurent))

                    if skipPostponement:
                        currentPairdOrder.append(D)
                    else:
                        if self.Postponement(P_hat, D):
                            P_hat.append(D)
                        else:
                            while (D['order_request_time'] - P_hat[0]['order_request_time']) >= self.t_Pmax:
                                PairdDriverId = self.FindVehicle(P_hat[0])
                                P_hat[0]['driver_id'] = str(currentDriverList[PairdDriverId]['Driver_ID'])
                                driverList[PairdDriverId]['Capacity'] += 1
                                PairedRestaurent = copy.deepcopy(next(filter(lambda x: int(x['Restaurant_ID']) == int(
                                    order["order_restaurant_carrier_restaurantId"]), restaurantList), None))
                                driverList[PairdDriverId]['Route'] = copy.deepcopy(
                                    self.AssignOrder(P_hat[0], currentDriverList[PairdDriverId], PairedRestaurent))
                                pairdOrder.append(P_hat[0])
                                P_hat.pop(0)
                                if len(P_hat) == 0:
                                    break
                            if len(P_hat) >= self.maxLengthPost:
                                for order in P_hat:
                                    PairedRestaurent = copy.deepcopy(
                                        next(filter(lambda x: int(x['Restaurant_ID']) == int(
                                            order["order_restaurant_carrier_restaurantId"]), restaurantList),
                                             None))
                                    PairdDriverId = self.FindVehicle(order, PairedRestaurent,
                                                                     currentDriverList)
                                    currentDriverList[PairdDriverId]['Capacity'] += 1
                                    order['driver_id'] = str(currentDriverList[PairdDriverId]['Driver_ID'])
                                    PairedRestaurent['orderId'] = (order['_id'])
                                    currentDriverList[PairdDriverId]['Route'] = copy.deepcopy(
                                        self.AssignOrder(order, currentDriverList[PairdDriverId],
                                                         PairedRestaurent))
                                    pairdOrder.append(order)
                                P_hat.clear()
                            P_hat.append(D)
                    S = self.TotalDelay(driverList)
                currentSlack = self.Slack(driverList)
                if (S < delay) or ((S == delay) and (currentSlack < slack)):
                    slack = currentSlack
                    delay = S
                    driverList = copy.deepcopy(currentDriverList)
                    postponedOrder = copy.deepcopy(P_hat)
                    pairdOrder = copy.deepcopy(currentPairdOrder)
            for order in postponedOrder:
                currentPairedDriver = next(filter(lambda driver: str(driver['Driver_ID']) == str(order['driver_id']), driverList))
                currentPairedDriverId = driverList.index(currentPairedDriver) if currentPairedDriver in driverList else -1
                driverList[currentPairedDriverId]['Route'] = copy.deepcopy(list(filter(lambda x: (int(x['nodeType']) == 0 and x['order_id'] != order['_id'])or (int(x['nodeType']) == 1 and str(x['_id']) != str(order['_id'])),driverList[currentPairedDriverId]['Route'])))

            self.updateOrder(driverList)
            self.updatePosponedOrder(postponedOrder)
            self.updatePairdOrder(pairdOrder)
            print("Thread:", index, " is finished")
        except Exception as e:
            logging.critical(e, exc_info=True)

    def deltaSDelay(self, route, Longitude, Latitude):
        try:
            delay: float = 0.0
            tripTime: float = 0.0
            currentRoute = copy.deepcopy(route)
            currentRoute.insert(0, {"Longitude": Longitude, "Latitude": Latitude, 'nodeType': 2})
            for i in range(1, len(currentRoute), 1):
                previousNode = currentRoute[i - 1]
                currentNode = currentRoute[i]
                currentDistance = self.distance(float(previousNode['Latitude']), float(previousNode['Longitude']),
                                                float(currentNode['Latitude']), float(currentNode['Longitude']))
                tripTime += currentDistance / self.velocity
                if 'order_request_time' in currentNode:
                    timeComplete = timedelta(seconds=tripTime) + self.time_buffer + datetime.now() + timedelta(hours=8)
                    timeDeadline = currentNode['order_request_time'] + self.deadlineTime
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

                pairedDriver['Route'][0]['nodeType'] = 0
                pairedDriver['Route'][0]['order_id'] = order['_id']

                pairedDriver['Route'][1]['nodeType'] = 1

            else:
                first: int = 0
                second: int = 1
                minDelayTime = float('inf')
                for i in range(0, len(pairedDriver['Route']), 1):
                    for j in range(i + 1, len(pairedDriver['Route']) + 2, 1):

                        tmpDriver = copy.deepcopy(pairedDriver)
                        tmpDriver['Route'].insert(i, currentParedRestaurent)
                        tmpDriver['Route'].insert(j, order)
                        delayTime = self.deltaSDelay(tmpDriver['Route'], tmpDriver['Latitude'], tmpDriver['Longitude'])

                        if minDelayTime > delayTime:
                            minDelayTime = delayTime
                            first = i
                            second = j

                pairedDriver['Route'].insert(first, currentParedRestaurent)
                pairedDriver['Route'][first]['nodeType'] = 0
                pairedDriver['Route'][first]['order_id'] = order['_id']

                pairedDriver['Route'].insert(second, order)
                pairedDriver['Route'][second]['nodeType'] = 1
            return pairedDriver['Route']
        except Exception as e:
            logging.critical(e, exc_info=True)

    # main function

    def Slack(self, driverList):
        return sum(self.slackDelay(driver['Route'], driver['Latitude'], driver['Longitude']) for driver in driverList)

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

    def slackDelay(self, route, Longitude, Latitude):
        try:
            delay: int = 0
            tripTime: int = 0
            currentRoute: list = copy.deepcopy(route)
            currentRoute.insert(0, {"Longitude": Longitude, "Latitude": Latitude, 'nodeType': 2})
            for i in range(1, len(currentRoute), 1):
                currentDistance = self.distance(float(currentRoute[i - 1]['Latitude']),
                                                float(currentRoute[i - 1]['Longitude']),
                                                float(currentRoute[i]['Latitude']), float(currentRoute[i]['Longitude']))
                tripTime += currentDistance / self.velocity
                if 'restaurantId' in currentRoute[i]:
                    deadLine = currentRoute[i]['deadLineTime'] - datetime.now() + timedelta(hours=8)
                    delayTime = timedelta(seconds=tripTime) - timedelta(seconds=self.time_buffer) - deadLine
                    delay += max(0.0, delayTime.total_seconds())
            return delay
        except Exception as e:
            logging.critical(e, exc_info=True)

    def TotalDelay(self, driverList):
        try:
            return sum(
                self.deltaSDelay(driver['Route'], driver['Longitude'], driver['Latitude']) for driver in driverList)
        except Exception as e:
            logging.critical(e, exc_info=True)

    def Postponement(self, P_hat, D):
        try:
            if len(P_hat) < self.maxLengthPost or D['order_request_time'] - P_hat[0][
                'order_request_time'] < self.t_Pmax:  # if postponement set is empty
                return True
            else:
                return False
        except Exception as e:
            logging.critical(e, exc_info=True)

    def distance(self, lat1, lon1, lat2, lon2):
        try:

            a = 0.5 - math.cos((lat2 - lat1) * self.p) / 2 + math.cos(lat1 * self.p) * math.cos(lat2 * self.p) * (
                    1 - math.cos((lon2 - lon1) * self.p)) / 2
            return 12742 * math.asin(math.sqrt(a))  # 2*R*asin...
        except Exception as e:
            logging.critical(e, exc_info=True)

    def updateOrder(self, driverList):
        try:
            updatedDriver = list(filter(lambda driver: len(driver['Route']) > 0, driverList))
            for driver in updatedDriver:
                self.driverCollection.update_one({
                    'Driver_ID': driver['Driver_ID']
                }, {
                    "$set": {
                        'Capacity': driver['Capacity'],
                        'Velocity': driver['Velocity'],
                        'Route': driver['Route']
                    },
                    "$currentDate": {
                        "lastModified": True
                    }
                })
        except Exception as e:
            logging.critical(e, exc_info=True)

    def updatePosponedOrder(self, pospondList):

        for order in pospondList:
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

    def updatePairdOrder(self, pairedOrderList):
        for pairedOrder in pairedOrderList:
            try:
                self.orderCollection.update_one({
                    '_id': pairedOrder['_id']
                }, {
                    '$set': {
                        'order_approved_at':datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                        'order_status': 'headToRes',
                        'driver_id': pairedOrder['driver_id']
                    }
                }, upsert=False)
            except Exception as e:
                logging.critical(e, exc_info=True)


test = RMDP()
test.generateThread()