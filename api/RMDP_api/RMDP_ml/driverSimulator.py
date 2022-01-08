# from generatingData import generateTestData
# from Math.Geometry import interSectionCircleAndLine
import logging
import os
from concurrent.futures import ThreadPoolExecutor
import copy
from datetime import datetime
# from Math import Geometry

from Database_Operator.Mongo_Operator import Mongo_Operate
from Math import Geometry


class driverSimulator:
    def __init__(self, cityIndex, restaurant_prepareTime, velocity, deadline, capacity, q_table):
        self.totalCurrentWorker = 2
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
        self.DBclient = Mongo_Operate()
        self.updateTime = 1
        self.time_tik = 0
        self.driverList = []
        self.cityList = self.DBclient.getAllCity()  # get all citye
        self.cityIndex = cityIndex
        self.restaurantList = self.DBclient.getRestaurantListBaseOnCity(self.cityList[self.cityIndex]['City'])
        self.orders = []
        self.driverList = []
        self.onTime = 0
        self.outTime = 0
        self.orderOnWay = 0
        self.restaurantPrepareTime = restaurant_prepareTime*60
        self.deadlineTime = deadline * 60
        self.velocity = velocity*0.2777777777777778
        self.c = 0
        self.qtable = q_table

    def generateThread(self, time_tik, orders, driverList):
        self.time_tik = time_tik
        totalCurrentWorker = 1
        logging.info("start generating")
        with ThreadPoolExecutor(max_workers=totalCurrentWorker) as executor:
            threads = []
            self.orders = copy.deepcopy(orders)
            self.driverList = copy.deepcopy(driverList)
            threads.append(executor.submit(self.updateDriverLocation, cityName=(self.cityList[self.cityIndex])))
        logging.info("task completed")
    def update(self):
        total_dis = 0
        for driver in self.driverList:
            total_dis+=driver['State']
            driver['Reward']=total_dis
            self.DBclient.updateDriver(driver)
        for order in self.orders:
            self.DBclient.updateOrder(order)
    def getDriver(self):
        self.driverList = self.DBclient.getDriverBaseOnCity(self.city['City'])

    def updateDriverLocation(self, cityName):
        try:
            for currentDriver in self.driverList:
                if currentDriver['Capacity'] > 0:
                    targetDestination = currentDriver['Route'][0]
                    # distance between target distance and current driver
                    DistanceRemain = Geometry.coorDistance(currentDriver['Latitude'],
                                                           currentDriver['Longitude'],
                                                           targetDestination['Latitude'],
                                                           targetDestination['Longitude'])
                    # the distance of each update time
                    DistanceTraveled = (currentDriver['Velocity'] / 1000 * self.updateTime)
                    # transform distance to degree
                    # the driver update distance longer than next destination
                    if DistanceTraveled >= DistanceRemain:
                        currentDriver['Latitude'] = targetDestination['Latitude']
                        currentDriver['Longitude'] = targetDestination['Longitude']
                        travelLocation = currentDriver['Route'][0]
                        currentOrder = 0
                        for i in self.orders:
                            if i['Order_ID'] == travelLocation['Order_ID']:
                                currentOrder=i
                                break
                        if travelLocation['nodeType'] == 0:
                            if (currentOrder['order_request_time']+self.restaurantPrepareTime)>self.time_tik:
                                currentOrder['order_status'] = 'WaitForMeal'
                            else:
                                currentDriver['Route'].pop(0)
                                currentOrder['order_status'] = 'headToCus'
                                currentOrder['order_restaurant_carrier_date'] = self.time_tik
                                self.c+=1
                        else:
                            currentDriver['Route'].pop(0)
                            currentOrder['order_status'] = 'delivered'
                            currentDriver['Capacity'] -= 1
                            if currentOrder['order_request_time'] + self.deadlineTime >= self.time_tik:
                                self.onTime+=1
                            else:
                                self.outTime+=1
                            self.orderOnWay-=1
                            currentOrder['order_delivered_customer_date'] = self.time_tik
                        if currentDriver['Route'] is None:
                            currentDriver['Velocity'] = 0
                        currentDriver['State'] += DistanceRemain
                    else:
                        updatedLat, updatedLon = Geometry.interSectionCircleAndLine(currentDriver['Latitude'],
                                                                                    currentDriver['Longitude'],
                                                                                    DistanceTraveled,
                                                                                    currentDriver['Latitude'],
                                                                                    currentDriver['Longitude'],
                                                                                    targetDestination['Latitude'],
                                                                                    targetDestination['Longitude'],
                                                                                    DistanceRemain)

                        currentDriver['Latitude'] = updatedLat
                        currentDriver['Longitude'] = updatedLon
                        currentDriver['State'] += DistanceTraveled
                #q-table move
                else:
                    now_state = self.compu(currentDriver, cityName)
                    next_state = [0,0]
                    now_reward = -1
                    targetDestination = {'Latitude':0, 'Longitude':0}
                    for i in range(0,3):
                        for j in range(0,3):
                            a = now_state[0]
                            b = now_state[1]
                            if i == 1:
                                a += 1
                            elif i == 2:
                                a -= 1
                            if j == 1:
                                b += 1
                            elif j == 2:
                                j -= 1
                            if a*50+b >= 0 and a*50+b <= 2499 and self.qtable[a*50+b][1] > now_reward:
                                now_reward = self.qtable[a*50+b][1]
                                next_state[0] = a
                                next_state[1] = b
                    targetDestination['Latitude'] = cityName['Latitude'] - cityName['radius'] + next_state[0] * (
                                cityName['radius'] * 2 / 50) + cityName['radius']/50
                    targetDestination['Longitude'] = cityName['Longitude'] - cityName['radius'] + next_state[1] * (
                                cityName['radius'] * 2 / 50) + cityName['radius']/50
                    #print(targetDestination)
                    DistanceRemain = Geometry.coorDistance(currentDriver['Latitude'],
                                                           currentDriver['Longitude'],
                                                           targetDestination['Latitude'],
                                                           targetDestination['Longitude'])
                    DistanceTraveled = (self.velocity / 1000 * self.updateTime)
                    if DistanceRemain <= DistanceTraveled:
                        currentDriver['Latitude']= targetDestination['Latitude']
                        currentDriver['Longitude'] = targetDestination['Longitude']
                    else:
                        updatedLat, updatedLon = Geometry.interSectionCircleAndLine(currentDriver['Latitude'],
                                                                                    currentDriver['Longitude'],
                                                                                    DistanceTraveled ,
                                                                                    currentDriver['Latitude'],
                                                                                    currentDriver['Longitude'],
                                                                                    targetDestination['Latitude'],
                                                                                    targetDestination['Longitude'],
                                                                                    DistanceRemain)
                        currentDriver['Latitude'] = updatedLat
                        currentDriver['Longitude'] = updatedLon
        except Exception as e:
            logging.critical(e, exc_info=True)

    def compu(self, res, city):
        state = [
            int(abs(float(city['Latitude']) - float(city['radius']) - float(res['Latitude'])) / (
                    float(city['radius']) * 2 / 50)),
            int(abs(float(city['Longitude']) - float(city['radius']) - float(res['Longitude'])) / (
                    float(city['radius']) * 2 / 50))]
        if state[0] > 49:
            state[0] = 49
        elif state[0] < 0:
            state[0] = 0
        if state[1] > 49:
            state[1] = 49
        elif state[1] < 0:
            state[1] = 0
        return state

    def computeState(self, agent, city):
        state = [
            int(abs(float(city['Latitude']) - float(city['radius']) - float(agent['Latitude'])) / (
                    float(city['radius']) * 2 / 50)),
            int(abs(float(city['Longitude']) - float(city['radius']) - float(agent['Longitude'])) / (
                    float(city['radius']) * 2 / 50))]
        if state[0] > 49:
            state[0] = 49
        elif state[0] < 0:
            state[0] = 0
        if state[1] > 49:
            state[1] = 49
        elif state[1] < 0:
            state[1] = 0
        return_state = state[0] * 50 + state[1]
        return return_state



#test = driverSimulator()
#test.generateThread()
