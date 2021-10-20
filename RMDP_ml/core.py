import copy
import logging
import math
import os
import random
from datetime import datetime, timedelta, time
import numpy as np
from RMDP_ml.Math import Geometry
from RMDP_ml.Database_Operator import Mongo_Operator

DEBUG = False if int(os.environ['DEBUG']) == 1 else True
S = 0
time_buffer = timedelta(minutes=0)
t_Pmax = timedelta(seconds=40)
t_ba = 10
delay = 5
capacity = 5
velocity: float = 50 * 0.2777777777777778
restaurantPrepareTime = timedelta(minutes=20)
deadlineTime = timedelta(minutes=40)
p = math.pi / 180


def generateThread():
    cityList = Mongo_Operator.getAllCity()
    np.apply_along_axis(sequencePermutation, axis=1, arr=cityList)


def sequencePermutation(city):
    try:
        # parameter init
        # initT = 1000
        initT = 200
        minT = 1
        iterL = 10
        eta = 0.95
        k = 1
        # RMDP setting
        pairdOrder = []
        # simulated annealing
        t = initT
        counter = 0
        skipPostponement = False
        pairdOrder = []
        maxLengthPost = 5

        restaurantList = Mongo_Operator.getRestaurantListBaseOnCity(city[0])
        driverList = Mongo_Operator.getDriverBaseOnCity(city[0])
        filterrestTaurantCode = restaurantList[:, 0].tolist()
        unAssignOrder = Mongo_Operator.getOrderBaseOnCity(filterrestTaurantCode, "unassigned")  # get unassigned order
        postponedOrder = Mongo_Operator.getOrderBaseOnCity(filterrestTaurantCode, "waiting")  # get postpone order
        finishedOrder = Mongo_Operator.getOrderBaseOnCity(filterrestTaurantCode, "delivered")
        nonUpdateOrder = finishedOrder[finishedOrder['Qtable_updated'] == 0]
        q_setting = Mongo_Operator.getQlearning(city['City'])
        updateRealReward(nonUpdateOrder, restaurantList, q_setting)
        if len(unAssignOrder) == 0 and len(postponedOrder) > 0:
            skipPostponement = True
            unAssignOrder = postponedOrder.copy()
            postponedOrder.clear()
        if maxLengthPost <= len(unAssignOrder):
            maxLengthPost = len(unAssignOrder) + 1
        # print(len(unAssignOrder))
        old_sequence = unAssignOrder.copy()
        delay_old, dr_list, post_list, paird_list, q_list = runRMDP(city, old_sequence,
                                                                    postponedOrder, driverList, restaurantList,
                                                                    pairdOrder, skipPostponement,
                                                                    maxLengthPost, q_setting)
        start = time.time()
        # delay = 0
        while t > minT and len(old_sequence) > 1:
            for _ in range(iterL):  # MonteCarlo method reject propblity
                position_switch1 = 0
                position_switch2 = random.randint(1, len(unAssignOrder) - 1)
                new_sequence = copy.deepcopy(old_sequence)
                new_sequence[position_switch1], new_sequence[position_switch2] = new_sequence[position_switch2], \
                                                                                 new_sequence[position_switch1]
                delay_new, driverList_new, postponedOrder_new, pairdorder_new, q_setting_new = runRMDP(
                    city,
                    old_sequence,
                    postponedOrder,
                    driverList,
                    restaurantList,
                    pairdOrder,
                    skipPostponement,
                    maxLengthPost,
                    q_setting)
                res = delay_new - delay_old
                if res < 0 or math.exp(-res / (k * t)) > random.uniform(0, 1):
                    old_sequence = copy.deepcopy(new_sequence)
                    delay_old = delay_new
                    dr_list = copy.deepcopy(driverList_new)
                    post_list = copy.deepcopy(postponedOrder_new)
                    paird_list = copy.deepcopy(pairdorder_new)
                    q_list = copy.deepcopy(q_setting_new)
                counter += 1
                end = time.time()
                if end - start > 10:
                    break
                t = t * eta

            driverList = copy.deepcopy(dr_list)
            postponedOrder = copy.deepcopy(post_list)
            pairdOrder = copy.deepcopy(paird_list)
            q_setting = copy.deepcopy(q_list)

            for order in postponedOrder:
                '''
                currentPairedDriver = next(
                    driver for driver in driverList if str(driver['Driver_ID']) == str(order['driver_id']))
                '''
                index = 0
                for driver in range(0, len(driverList)):
                    if driverList[driver]['Driver_ID'] == order['driver_id']:
                        index = driver
                        break
                '''
                currentPairedDriverId = driverList.index(
                    currentPairedDriver) if currentPairedDriver in driverList else -1
                '''
                '''
                driverList[currentPairedDriverId]['Route'] = copy.deepcopy(list(filter(
                    lambda x: (int(x['nodeType']) == 0 and x['Order_ID'] != order['Order_ID']) or (  # why no string
                            int(x['nodeType']) == 1 and str(x['Order_ID']) != str(order['Order_ID'])),
                    driverList[currentPairedDriverId]['Route'])))
                driverList[currentPairedDriverId]['Capacity'] -= 1
                '''
            driverList[index]['Route'] = copy.deepcopy(list(filter(
                lambda x: (int(x['nodeType']) == 0 and x['Order_ID'] != order['Order_ID']) or (  # why no string
                        int(x['nodeType']) == 1 and str(x['Order_ID']) != str(order['Order_ID'])),
                driverList[index]['Route'])))
            # driverList[index]['Capacity'] -= 1
            updateDriver(driverList)
            updatePosponedOrder(postponedOrder)
            updatePairdOrder(pairdOrder)
            Mongo_Operator.updateQlearning(q_setting)
    except Exception as e:
        logging.critical(e, exc_info=True)


def runRMDP(cityName, unAssignOrder, postponedOrder, driverList, restaurantList, pairdOrder, skipPostponement,
            maxLengthPost, q_setting):
    currentDriverList = driverList.copy()
    P_hat = postponedOrder.copy()  # waitting order
    currentPairdOrder = pairdOrder.copy()
    currentQ_setting = q_setting.copy()
    for D in unAssignOrder.iloc:
        currentPairdRestaurent = restaurantList[
            restaurantList['Restaurant_ID'] == D["order_restaurant_carrier_restaurantId"]]
        if skipPostponement:
            currentPairdDriverId, currentQ_setting, D = Qing(D, currentPairdRestaurent, currentDriverList,
                                                             cityName,
                                                             currentQ_setting)
            D["driver_id"] = currentDriverList[currentPairdDriverId]['Driver_ID']
            currentDriverList[currentPairdDriverId]['Capacity'] += 1  # why assign twice
            currentDriverList[currentPairdDriverId]['Route'] = copy.deepcopy(
                AssignOrder(D, currentDriverList[currentPairdDriverId], currentPairdRestaurent))
            currentPairdOrder.append(D)
        elif Postponement(P_hat, D, maxLengthPost):
            P_hat.append(D)
        else:
            while D['order_request_time'] - P_hat[0]['order_request_time'] >= t_Pmax and len(P_hat) > 0:
                PairedRestaurent = copy.deepcopy(next(restaurant for restaurant in restaurantList if
                                                      restaurant['Restaurant_ID'] == P_hat[0][
                                                          "order_restaurant_carrier_restaurantId"]
                                                      ))
                PairdDriverId, currentQ_setting, D = Qing(D, PairedRestaurent, currentDriverList, cityName,
                                                          currentQ_setting)
                P_hat[0]['driver_id'] = str(currentDriverList[PairdDriverId]['Driver_ID'])
                currentDriverList[PairdDriverId]['Capacity'] += 1
                currentDriverList[PairdDriverId]['Route'] = copy.deepcopy(
                    AssignOrder(P_hat[0], currentDriverList[PairdDriverId], PairedRestaurent))
                currentPairdOrder.append(P_hat[0])  # add finish order
                P_hat.pop(0)

            if len(P_hat) >= maxLengthPost:
                for order in P_hat:
                    PairedRestaurent = copy.deepcopy(next(
                        restaurant for restaurant in restaurantList if int(restaurant['Restaurant_ID']) == int(
                            order["order_restaurant_carrier_restaurantId"])))
                    PairdDriverId, currentQ_setting, D = Qing(D, PairedRestaurent, currentDriverList,
                                                              cityName, currentQ_setting)
                    currentDriverList[PairdDriverId]['Capacity'] += 1
                    order['driver_id'] = str(currentDriverList[PairdDriverId]['Driver_ID'])
                    currentDriverList[PairdDriverId]['Route'] = copy.deepcopy(
                        AssignOrder(order, currentDriverList[PairdDriverId], PairedRestaurent))
                    currentPairdOrder.append(order)
                P_hat.clear()
            P_hat.append(D)
        return TotalDelay(currentDriverList), currentDriverList, P_hat, currentPairdOrder, currentQ_setting


def deltaSDelay(self, route, Longitude, Latitude):
    delay: float = 0.0
    tripTime: float = 0.0
    currentRoute = copy.deepcopy(route)
    currentRoute.insert(0, {"Longitude": Longitude, "Latitude": Latitude, 'nodeType': 2})
    for i in range(1, len(currentRoute), 1):
        previousNode = currentRoute[i - 1]
        currentNode = currentRoute[i]
        currentDistance = Geometry.coorDistance(float(previousNode['Latitude']),
                                                float(previousNode['Longitude']),
                                                float(currentNode['Latitude']), float(currentNode['Longitude']))
        tripTime += currentDistance / self.velocity
        if 'order_request_time' in currentNode:
            timeComplete = timedelta(seconds=tripTime) + self.time_buffer + datetime.now() + timedelta(hours=8)
            timeDeadline = currentNode['order_request_time'] + self.deadlineTime
            timeDelay = timeComplete - timeDeadline
            delay += timeDelay.total_seconds()
    return max(0, delay)


def AssignOrder(self, order, pairedDriver, currentParedRestaurent):
    try:
        if not pairedDriver['Route']:
            pairedDriver['Route'].append(currentParedRestaurent)
            pairedDriver['Route'].append(order)

            pairedDriver['Route'][0]['nodeType'] = 0
            pairedDriver['Route'][0]['Order_ID'] = order['Order_ID']

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
            pairedDriver['Route'][first]['Order_ID'] = order['Order_ID']
            pairedDriver['Route'].insert(second, order)
            pairedDriver['Route'][second]['nodeType'] = 1
        return pairedDriver['Route']
    except Exception as e:
        logging.critical(e, exc_info=True)


def Slack(driverList):
    return sum(slackDelay(driver['Route'], driver['Latitude'], driver['Longitude']) for driver in driverList)


def tripTime(driv, res, order):
    try:
        disDriver2Res = Geometry.coorDistance(float(driv['Latitude']), float(driv['Longitude']),
                                              # get distance d->r
                                              float(res['Latitude']),
                                              float(res['Longitude']))
        Res2Delivery = Geometry.coorDistance(float(res['Latitude']), float(res['Longitude']),  # get distance r->o
                                             float(order['Latitude']),
                                             float(order['Longitude']))
        return float(disDriver2Res + Res2Delivery / float(velocity))  # time
    except Exception as e:
        logging.critical(e, exc_info=True)


def FindVehicle(Order, OrderRestaurant, driverList):
    try:
        handleDriver = list(filter(lambda driver: int(driver['Capacity']) < int(capacity),
                                   driverList))  # get less than capacity driver
        distanceList = list(
            map(lambda x: tripTime(x, OrderRestaurant, Order), handleDriver))  # getall triptime
        return distanceList.index(min(distanceList))  # return min driver in index
    except Exception as e:
        logging.critical(e, exc_info=True)


def slackDelay(self, route, Longitude, Latitude):
    delay: int = 0
    tripTime: int = 0
    currentRoute: list = copy.deepcopy(route)
    currentRoute.insert(0, {"Longitude": Longitude, "Latitude": Latitude, 'nodeType': 2})
    for i in range(1, len(currentRoute), 1):
        currentDistance = Geometry.coorDistance(float(currentRoute[i - 1]['Latitude']),
                                                float(currentRoute[i - 1]['Longitude']),
                                                float(currentRoute[i]['Latitude']), float(currentRoute[i]['Longitude']))
        tripTime += currentDistance / self.velocity
        if 'restaurantId' in currentRoute[i]:
            deadLine = currentRoute[i]['deadLineTime'] - datetime.now() + timedelta(hours=8)
            delayTime = timedelta(seconds=tripTime) - timedelta(seconds=self.time_buffer) - deadLine
            delay += max(0.0, delayTime.total_seconds())
    return delay


def TotalDelay(driverList):
    return sum(deltaSDelay(driver['Route'], driver['Longitude'], driver['Latitude']) for driver in driverList)


def Postponement(P_hat, D, maxLengthPost):
    return True if len(P_hat) < maxLengthPost and D['order_request_time'] - P_hat.iloc[0][
        'order_request_time'] < t_Pmax else False


def updateDriver(driverList):
    for driver in list(filter(lambda driver: len(driver['Route']) > 0, driverList)):
        driver['Velocity'] = velocity
        Mongo_Operator.updateDriver(driver)


def updatePosponedOrder(pospondList):
    for order in pospondList:
        order['order_status'] = 'waiting'
        Mongo_Operator.updateOrder(order)


def updatePairdOrder(self, pairedOrderList):
    for order in pairedOrderList:
        order['order_status'] = 'headToRes'
        order['order_approved_at'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        order['order_estimated_delivery_date'] = (datetime.now() + self.deadlineTime).strftime("%d-%m-%Y %H:%M:%S")
        self.DBclient.updateOrder(order)


def Qing(self, Ds_0, restaurant, drlist, city, q_setting):
    low_capacity = min(driver['Capacity'] for driver in drlist)
    if low_capacity < self.capacity:
        filteredDriver = list(filter(lambda driver: driver['Capacity'] == low_capacity, drlist))
        for v in filteredDriver:
            v['delay'] = self.deltaSDelay(v['Route'], v['Longitude'], v['Latitude'])
            v['dist'] = Geometry.coorDistance(v['Latitude'], v['Longitude'], float(restaurant['Latitude']),
                                              float(restaurant['Longitude']))
            filteredDriver = sorted(filteredDriver, key=lambda driver: (driver['delay'], driver['dist']))
            agents = filteredDriver[:] if len(filteredDriver) > 5 else filteredDriver[0:5]
            selectedAgent = next((agent for agent in agents if self.computeAction(agent, city, q_setting) == 1),
                                 agents[0])
            action = 1
            state = self.computeState(selectedAgent, city)
            if low_capacity > 0:
                for i in range(0, len(drlist)):
                    if drlist[i]['Driver_ID'] == selectedAgent['Driver_ID']:
                        old_state = drlist[i]['State']
                        old_reward = drlist[i]['Reward']
                        q_setting['q_table'][old_state][1] = old_reward  # state write back to qtable
                        drlist[i]['State'] = state  # get new state status
                        drlist[i]['Reward'] = q_setting['q_table'][state][1]  # current state old reward
                        break

            Ds_0['Qtable_position'] = state

            new_state = self.computeState(Ds_0, city)
            res2orderDist = Geometry.coorDistance(float(restaurant['Latitude']), float(restaurant['Longitude']),
                                                  float(Ds_0['Latitude']), float(Ds_0['Longitude']))
            res2orderDistTime = ((res2orderDist * 111 / self.velocity) * 60 + 20)
            reward = res2orderDist / res2orderDistTime

            action_0 = q_setting['q_table'][new_state][0]
            action_1 = q_setting['q_table'][new_state][1]
            max = 0
            if action_0 > action_1:
                max = action_0
            elif action_0 < action_1:
                max = action_1
            else:
                max = action_0 if random.randint(0, 1) else action_1
            q_setting['q_table'][state][action] = q_setting['q_table'][state][action] \
                                                  + q_setting['learning_rate'] * (
                                                          reward + q_setting['gamma'] * max -
                                                          q_setting['q_table'][state][action])

            return_index = next(
                (index for (index, d) in enumerate(drlist) if d['Driver_ID'] == selectedAgent['Driver_ID']), None)
            # reward = resturant&delivery distance / finish time
            q_setting['episode'] += 1
            # reduce episode
            q_setting['epsilon'] = q_setting['min_epislon'] + (
                    q_setting['max_epislon'] - q_setting['min_epislon']) * math.exp(
                -q_setting['decay_rate'] * q_setting['episode'])
            self.DBclient.updateQlearning(q_setting)
            return return_index


def real_reward(order, reward, q_setting):
    q_setting['q_table'][order['Qtable_position']][1] = reward
    order['Qtable_updated'] = 1
    Mongo_Operator.updateOrder(order)
    Mongo_Operator.updateQlearning(q_setting)


def updateRealReward(finishOrder, restaurantList, q_setting):
    for forder in finishOrder.iloc:
        targetRestaurant = restaurantList[
            restaurantList.Restaurant_ID == forder["order_restaurant_carrier_restaurantId"]]
        time = datetime.strptime(forder['order_restaurant_carrier_date'], "%Y-%m-%d %H:%M:%S") - forder[
            'order_request_time']
        distance = Geometry.coorDistance(targetRestaurant['Latitude'], targetRestaurant['Longitude'],
                                         forder['Latitude'], forder['Longitude'])  # meter
        reward = distance / (time.total_seconds() / 60)  # meter/second
        real_reward(forder, reward, q_setting)


def computeAction(self, agent, city, q_setting):
    state = self.computeState(agent, city)
    exp_exp_tradeoff = random.uniform(0, 1)
    if exp_exp_tradeoff > q_setting['epsilon'] and q_setting['q_table'][state][0] != q_setting['q_table'][state][1]:
        return 0 if q_setting['q_table'][state][0] > q_setting['q_table'][state][1] else 1
    else:
        return random.randint(0, 1)


def computeState(agent, city):
    state = [int(abs(float(city['Latitude']) - float(city['radius']) - float(agent['Latitude'])) / (
            float(city['radius']) * 2 / 50)),
             int(abs(float(city['Longitude']) - float(city['radius']) - float(agent['Longitude'])) / (
                     float(city['radius']) * 2 / 50))]
    return state[0] * 50 + state[1]

