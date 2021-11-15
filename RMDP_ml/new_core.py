import copy
import logging
import math
import os
import random
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta, time
import numpy as np
from RMDP_ml.Math import Geometry
from RMDP_ml.Database_Operator import Mongo_Operator
from concurrent.futures import ThreadPoolExecutor
import time

DEBUG = False if int(os.environ['DEBUG']) == 1 else True
S = 0
time_buffer = timedelta(minutes=0)
t_Pmax = timedelta(seconds=40)  # postponement_limit_time
t_ba = 10  # maxtime_of_system_get_order_to_finish_order
capacity = 5
velocity: float = 1000 * 0.2777777777777778
restaurantPrepareTime = timedelta(minutes=20)
deadlineTime = timedelta(minutes=40)
p = math.pi / 180
pairdDriverOnNumpyArray = {
    'Driver_ID': 0,
    'Country_Code': 1,
    'City_id': 2,
    'Longitude': 3,
    'Latitude': 4,
    'Velocity': 5,
    'Capacity': 6,
    'State': 7,
    'Reward': 8,
    'Node_ID': 9,
    'Node_num': 10
}
pairdRouteOnNumpyArray = {
    'Driver_ID': 0
    , 'Latitude': 1
    , 'Longitude': 2
    , 'nodetype': 3
    , 'Restaurant_ID': 4,
    'Order_ID': 5,
    'Node_ID': 6
    , 'delivered': 7
}
paridOrderOnNumpyArray = {
    'driver_id': 0,
    'order_approved_at': 1,
    'Latitude': 2,
    'Longitude': 3,
    'Order_ID': 4,
    'Qtable_position': 5,
    'order_delivered_customer_date': 6,
    'Qtable_updated': 7,
    'order_estimated_delivery_date': 8,
    'order_request_time': 9,
    'order_restaurant_carrier_date': 10,
    'order_restaurant_carrier_restaurantId': 11,
    'order_status': 12,
}
pairdCityOnNumpyArray = {
    'Country_Code': 0,
    'Latitude': 1,
    'Longitude': 2,
    'radius': 3,
    'City_id': 4
}
pairdRestaurantOnNumpyArray = {
    'Restaurant_ID': 0,
    'Longitude': 1,
    'Latitude': 2,
    'order_num': 3
}
pairdQlearningOnNumpyArray = {
    'City_id': 0,
    'state_index': 1,
    'action_index': 2,
    'q_table': 3,
    'center': 4,
    'side_length': 5,
    'learning_rate': 6,
    'gamma': 7,
    'epsilon': 8,
    'max_epislon': 9,
    'min_epislon': 10,
    'decay_rate': 11,
    'nearBY': 12,
    'episode': 13,
    'capacity': 14
}


def generateThread():
    cityList = Mongo_Operator.getAllCity()
    logging.info("start generating")
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
        pairdOrder = np.zeros(shape=(0, 13))
        nonUpdateOrder = np.zeros(shape=(0,13))
        # simulated annealing
        t = initT
        counter = 0
        skipPostponement = False
        pairdOrder = np.zeros(shape=(0, 13))
        maxLengthPost = 5
        over10s = False
        restaurantList = Mongo_Operator.getRestaurantListBaseOnCity(city[0])
        driverList = Mongo_Operator.getDriverBaseOnCity(city[0])
        filterrestTaurantCode = restaurantList[:, 0].tolist()
        unAssignOrder = Mongo_Operator.getOrderBaseOnCity(filterrestTaurantCode, 0)  # get unassigned order
        postponedOrder = Mongo_Operator.getOrderBaseOnCity(filterrestTaurantCode, 1)  # get postpone order
        finishedOrder = Mongo_Operator.getOrderBaseOnCity(filterrestTaurantCode, 4)
        q_setting = Mongo_Operator.getQlearning(city[0])
        route = driverHashTable(driverList)
        if len(finishedOrder) != 0:
            nonUpdateOrder = np.concatenate((nonUpdateOrder, finishedOrder[finishedOrder[:,7] ==0] ), axis=0)
            updateRealReward(nonUpdateOrder, restaurantList, q_setting)
        if len(unAssignOrder) == 0 and len(postponedOrder) > 0:
            skipPostponement = True
            unAssignOrder = postponedOrder.copy()
            postponedOrder = np.zeros(shape=(0, 13))
        if maxLengthPost <= len(unAssignOrder):
            maxLengthPost = len(unAssignOrder) + 1
        # print(len(unAssignOrder))
        old_sequence = unAssignOrder.copy()
        delay_old, dr_list, post_list, paird_list, q_list, update_route = runRMDP(city, old_sequence,
                                                                                  postponedOrder, driverList,
                                                                                  restaurantList,
                                                                                  pairdOrder, skipPostponement,
                                                                                  maxLengthPost, q_setting, route)
        start = time.time()
        # delay = 0
        while t > minT and len(old_sequence) > 1:
            for _ in range(iterL):  # MonteCarlo method reject propblity
                position_switch1 = 0
                position_switch2 = random.randint(1, len(unAssignOrder) - 1)
                new_sequence = copy.deepcopy(old_sequence)
                new_sequence[position_switch1], new_sequence[position_switch2] = new_sequence[position_switch2], \
                                                                                 new_sequence[position_switch1]
                delay_new, driverList_new, postponedOrder_new, pairdorder_new, q_setting_new, update_route_new = runRMDP(
                    city,
                    old_sequence,
                    postponedOrder,
                    driverList,
                    restaurantList,
                    pairdOrder,
                    skipPostponement,
                    maxLengthPost,
                    q_setting,
                    route
                )
                res = delay_new - delay_old
                if res < 0 or math.exp(-res / (k * t)) > random.uniform(0, 1):
                    old_sequence = copy.deepcopy(new_sequence)
                    delay_old = delay_new
                    dr_list = copy.deepcopy(driverList_new)
                    post_list = copy.deepcopy(postponedOrder_new)
                    paird_list = copy.deepcopy(pairdorder_new)
                    q_list = copy.deepcopy(q_setting_new)
                    update_route = copy.deepcopy(update_route_new)


                counter += 1
                end = time.time()

                if end - start > 10:
                    over10s = True
                    break
                t = t * eta
            if over10s:
                # print(end - start)
                break

        updateRoute(update_route, dr_list)
        updateDriver(dr_list)
        updatePosponedOrder(post_list)
        updatePairdOrder(paird_list)
        Mongo_Operator.updateQlearning(q_list)
    except Exception as e:
        logging.critical(e, exc_info=True)


def runRMDP(cityName, unAssignOrder, postponedOrder, driverList, restaurantList, pairdOrder, skipPostponement,
            maxLengthPost, q_setting, route):
    try:
        currentDriverList = driverList.copy()
        P_hat = postponedOrder.copy()  # waitting order
        currentPairdOrder = pairdOrder.copy()
        currentQ_setting = q_setting.copy()
        currentDriverRoute = route.copy()
        delays = 0
        ls = np.zeros(shape=(1, 0))
        for D in unAssignOrder:
            currentPairdRestaurent = next(restaurant for restaurant in restaurantList if restaurant[0] == D[11])
            if skipPostponement:
                currentPairdDriverId, currentQ_setting, D = Qing(D, currentPairdRestaurent, currentDriverList,
                                                                 cityName,
                                                                 currentQ_setting, currentDriverRoute)
                D[0] = currentDriverList[currentPairdDriverId][0]
                currentDriverList[currentPairdDriverId][6] += 1

                currentDriverRoute[D[0]] = np.copy(
                    AssignOrder(D, currentDriverList[currentPairdDriverId], currentPairdRestaurent,
                                currentDriverRoute[D[0]]))
                D = D.reshape(1, 13)
                currentPairdOrder = np.concatenate((currentPairdOrder, D), axis=0)

            elif Postponement(P_hat, D, maxLengthPost):
                D = D.reshape(1, 13)
                P_hat = np.concatenate((P_hat, D), axis=0)
            else:

                while len(P_hat) > 0 and D[9] - P_hat[0][9] >= t_Pmax:
                    PairedRestaurant = copy.deepcopy(next(restaurant for restaurant in restaurantList if
                                                          restaurant[0] == P_hat[0][11]
                                                          ))
                    PairdDriverId, currentQ_setting, P_hat[0] = Qing(P_hat[0], PairedRestaurant, currentDriverList,
                                                                     cityName,
                                                                     currentQ_setting, currentDriverRoute)
                    P_hat[0][0] = currentDriverList[PairdDriverId][0]
                    currentDriverList[PairdDriverId][6] += 1
                    currentDriverRoute[P_hat[0][0]] = np.copy(
                        AssignOrder(P_hat[0], currentDriverList[PairdDriverId], PairedRestaurant,
                                    currentDriverRoute[P_hat[0][0]]))
                    # a = P_hat[0].reshape(1,13)
                    currentPairdOrder = np.concatenate((currentPairdOrder, P_hat[0].reshape(1, 13)), axis=0)
                    P_hat = np.delete(P_hat, 0, axis=0)

                if len(P_hat) >= maxLengthPost:
                    for order in P_hat:
                        PairedRestaurent = copy.deepcopy(next(
                            restaurant for restaurant in restaurantList if int(restaurant[0]) == int(order[11])))
                        PairdDriverId, currentQ_setting, order = Qing(order, PairedRestaurent, currentDriverList,
                                                                      cityName, currentQ_setting, currentDriverRoute)
                        currentDriverList[PairdDriverId][6] += 1
                        order[0] = currentDriverList[PairdDriverId][0]  # driver id to order
                        currentDriverRoute[order[0]] = copy.deepcopy(
                            AssignOrder(order, currentDriverList[PairdDriverId], PairedRestaurent,
                                        currentDriverRoute[order[0]]))
                        order = order.reshape(1, 13)
                        currentPairdOrder = np.concatenate((currentPairdOrder, order), axis=0)
                    P_hat = np.zeros(shape=(0, 13))
                P_hat = np.concatenate((P_hat, D.reshape(1, 13)), axis=0)
        return TotalDelay(currentDriverList,
                          currentDriverRoute), currentDriverList, P_hat, currentPairdOrder, currentQ_setting, currentDriverRoute
    except Exception as e:
        logging.critical(e, exc_info=True)


def deltaSDelay(route, Latitude, Longitude):
    try:
        delay: float = 0.0
        tripTime: float = 0.0
        currentRoute = np.copy(route)
        # print(currentRoute)
        currentRoute = currentRoute[currentRoute[:, 6].argsort()]
        currentDriverLocation = np.array([0, Latitude, Longitude, 2, 0, 0, 0, 0])
        currentRoute = np.insert(currentRoute, 0, currentDriverLocation, axis=0)
        for i in range(1, len(currentRoute), 1):
            previousNode = currentRoute[i - 1]
            currentNode = currentRoute[i]
            currentDistance = Geometry.coorDistance(float(previousNode[1]),
                                                    float(previousNode[2]),
                                                    float(currentNode[1]), float(currentNode[2]))
            tripTime += currentDistance / velocity / 1000
            if currentNode[3] == 1:
                order = Mongo_Operator.getPairedOrderBaseOnOrderID(currentNode[5])
                timeComplete = timedelta(seconds=tripTime) + time_buffer + datetime.now() + timedelta(hours=8)

                timeDeadline = order[0][9] + deadlineTime
                timeDelay = timeComplete - timeDeadline
                delay += timeDelay.total_seconds()
        return max(0, delay)
    except Exception as e:
        logging.critical(e, exc_info=True)


def driverHashTable(driverlist):
    driverRoute = {}
    for driver in driverlist:
        getRoute = Mongo_Operator.getDriverRouteBaseOnDriverID(driver[0])
        driverRoute.setdefault(driver[0], getRoute)
    return driverRoute


def AssignOrder(order, pairedDriver, currentParedRestaurent, currentDriverRoute):  # route is paird driver's np array
    try:
        restaurantNode = np.array(
            [pairedDriver[0], currentParedRestaurent[2], currentParedRestaurent[1], 0, currentParedRestaurent[0],
             order[4], 1, 0]).reshape(1, 8)
        orderNode = np.array(
            [pairedDriver[0], order[2], order[3], 1, currentParedRestaurent[0], order[4], 2, 0]).reshape(1, 8)
        order1 = Mongo_Operator.getPairedOrderBaseOnOrderID(order[4])
        if len(currentDriverRoute) == 0:
            insertDriverRoute = np.concatenate((currentDriverRoute, restaurantNode), axis=0)
            insertDriverRoute = np.concatenate((insertDriverRoute, orderNode), axis=0)
            currentDriverRoute = insertDriverRoute
        else:

            currentDriverRoute[currentDriverRoute[:, 6].argsort()]  # sorting by node idf
            first = 0
            second = 1
            answerRoute = np.zeros(shape=(0, 8))
            minDelayTime = float('inf')
            for i in range(1, len(currentDriverRoute), 1):  # start 0 or 1 , we can't change 0 when delivered
                for j in range(i + 1, len(currentDriverRoute) + 1, 1):
                    tmpRoute = np.copy(currentDriverRoute)
                    tmpRoute = np.insert(tmpRoute, i, restaurantNode[0], axis=0)
                    tmpRoute = np.insert(tmpRoute, j, orderNode[0], axis=0)
                    for k in range(1, len(tmpRoute) + 1):
                        tmpRoute[k - 1][6] = k
                    delayTime = deltaSDelay(tmpRoute, pairedDriver[4], pairedDriver[3])
                    if minDelayTime > delayTime:
                        minDelayTime = delayTime
                        first = i
                        second = j
                        answerRoute = tmpRoute

            # restaurantNode[0][6] = first
            # orderNode[0][6] = second
            # insertDriverRoute = np.concatenate(( restaurantNode[0], orderNode[0]), axis=0)
            currentDriverRoute = answerRoute
        return currentDriverRoute  # dict, nparray
    except Exception as e:
        logging.critical(e, exc_info=True)


def Slack(driverList):
    return sum(slackDelay(driver['Route'], driver['Latitude'], driver['Longitude']) for driver in driverList)


def tripTime(driv, res, order):
    try:
        disDriver2Res = Geometry.coorDistance(float(driv[4]), float(driv[3]),
                                              # get distance d->r
                                              float(res[2]),
                                              float(res[1]))
        Res2Delivery = Geometry.coorDistance(float(res[2]), float(res[1]),  # get distance r->o
                                             float(order[2]),
                                             float(order[3]))
        return float(disDriver2Res + Res2Delivery / float(velocity))  # time
    except Exception as e:
        logging.critical(e, exc_info=True)


def FindVehicle(Order, OrderRestaurant, driverList):
    try:
        handleDriver = list(filter(lambda driver: int(driver[6]) < int(capacity),
                                   driverList))  # get less than capacity driver
        distanceList = list(
            map(lambda x: tripTime(x, OrderRestaurant, Order), handleDriver))  # getall triptime
        return driverList.index(min(distanceList))  # return min driver in index
    except Exception as e:
        logging.critical(e, exc_info=True)


def slackDelay(route, Longitude, Latitude):
    try:
        delay: int = 0
        tripTime: int = 0
        currentRoute: list = copy.deepcopy(route)
        currentDriverLocation = np.array([0, Latitude, Longitude, 2, 0, 0, 0, 0])
        currentRoute.insert(0, {"Longitude": Longitude, "Latitude": Latitude, 'nodeType': 2})
        for i in range(1, len(currentRoute), 1):
            currentDistance = Geometry.coorDistance(float(currentRoute[i - 1]['Latitude']),
                                                    float(currentRoute[i - 1]['Longitude']),
                                                    float(currentRoute[i]['Latitude']),
                                                    float(currentRoute[i]['Longitude']))
            tripTime += currentDistance / velocity
            if 'restaurantId' in currentRoute[i]:
                deadLine = currentRoute[i]['deadLineTime'] - datetime.now() + timedelta(hours=8)
                delayTime = timedelta(seconds=tripTime) - timedelta(seconds=time_buffer) - deadLine
                delay += max(0.0, delayTime.total_seconds())
        return delay
    except Exception as e:
        logging.critical(e, exc_info=True)


def TotalDelay(driverList, route):
    try:
        sum = 0
        for driver in driverList:
            n = route[driver[0]].size / 8
            if n < 1:
                continue
            else:
                sum += deltaSDelay(route[driver[0]], driver[4], driver[3])
        return sum
        # return sum(deltaSDelay(route[driver[0]], driver[4], driver[3]) for driver in driverList)
    except Exception as e:
        logging.critical(e, exc_info=True)


def Postponement(P_hat, D, maxLengthPost):
    if len(P_hat) == 0:
        return True
    return True if len(P_hat) < maxLengthPost and D[9] - P_hat[0][9] < t_Pmax else False


def updateDriver(driverList):
    try:
        for driver in list(filter(lambda driver: driver[6] > 0, driverList)):  # capacity
            driver[5] = velocity
            Mongo_Operator.updateDriver(driver)
    except Exception as e:
        logging.critical(e, exc_info=True)


def updatePosponedOrder(pospondList):
    try:
        for order in pospondList:
            order[12] = 1
            Mongo_Operator.updateOrder(order)
    except Exception as e:
        logging.critical(e, exc_info=True)

def updatePairdOrder(pairedOrderList):
    try:
        for order in pairedOrderList:
            order[12] = 2
            order[1] = datetime.now()
            order[8] = datetime.now() + deadlineTime
            Mongo_Operator.updateOrder(order)
    except Exception as e:
        logging.critical(e, exc_info=True)


def updateRoute(Route, driverlist):
    try:
        for driver in driverlist:
            n = Route[driver[0]].size / 8
            if n < 1:
                continue
            else:
                for node in Route[driver[0]]:
                    Mongo_Operator.updateRoute(node)
    except Exception as e:
        logging.critical(e, exc_info=True)


def Qing(Ds_0, restaurant, drlist, city, q_setting, allDriverRoute):
    try:
        low_capacity = min(driver[6] for driver in drlist)
        if low_capacity < capacity:
            filteredDriver = list(filter(lambda driver: driver[6] == low_capacity, drlist))
            for v in filteredDriver:
                Route = allDriverRoute[v[0]]
                delay = 0
                if len(Route) > 0:
                    delay = deltaSDelay(Route, v[4], v[3])  # v['Route'], v['Longitude'], v['Latitude']
                dist = Geometry.coorDistance(v[4], v[3], float(restaurant[2]),
                                             float(restaurant[1]))
                filteredDriver = sorted(filteredDriver, key=lambda driver: (delay, dist))
                agents = filteredDriver[:] if len(filteredDriver) < 5 else filteredDriver[0:5]
                selectedAgent = next((agent for agent in agents if computeAction(agent, city, q_setting) == 1),
                                     agents[0])
                action = 1
                state = computeState(selectedAgent, city)
                return_index = next(
                    (index for (index, d) in enumerate(drlist) if d[0] == selectedAgent[0]), None)
                if low_capacity > 0:
                    old_state = drlist[return_index][7]
                    old_reward = drlist[return_index][8]
                    q_setting[0][3][int(old_state)][1] = old_reward  # state write back to qtable

                    drlist[return_index][7] = state  # get new state status
                    drlist[return_index][8] = q_setting[0][3][state][1]  # current state old reward
                Ds_0[5] = state
                new_state = computeState(Ds_0, city)
                res2orderDist = Geometry.coorDistance(float(restaurant[2]), float(restaurant[1]),
                                                      float(Ds_0[2]), float(Ds_0[3]))
                res2orderDistTime = ((res2orderDist * 111 / velocity) * 60 + 20)
                reward = res2orderDist / res2orderDistTime
                # update q_table
                # print(new_state)
                action_0 = q_setting[0][3][new_state][0]
                action_1 = q_setting[0][3][new_state][1]

                if action_0 > action_1:
                    max = action_0
                elif action_0 < action_1:
                    max = action_1
                else:
                    max = action_0 if random.randint(0, 1) else action_1
                q_setting[0][3][state][action] = q_setting[0][3][state][action] \
                                                 + q_setting[0][6] * (
                                                         reward + q_setting[0][7] * max -
                                                         q_setting[0][3][state][action])

                # reward = resturant&delivery distance / finish time
                q_setting[0][13] += 1
                # reduce episode
                q_setting[0][8] = q_setting[0][10] + (
                        q_setting[0][9] - q_setting[0][10]) * math.exp(
                    -q_setting[0][11] * q_setting[0][13])

                return return_index, q_setting, Ds_0
    except Exception as e:
        logging.critical(e, exc_info=True)


def real_reward(order, reward, q_setting):
    try:
        q_setting[0][3][order[5]][1] = reward
        order[7] = 1
        Mongo_Operator.updateOrder(order)
        Mongo_Operator.updateQlearning(q_setting)
    except Exception as e:
        logging.critical(e, exc_info=True)


def updateRealReward(finishOrder, restaurantList, q_setting):
    try:
        for forder in finishOrder:
            targetRestaurant = next(restaurant for restaurant in restaurantList if restaurant[0] == forder[11])
            time = forder[10] - forder[9]
            distance = Geometry.coorDistance(targetRestaurant[2], targetRestaurant[1],
                                             forder[2], forder[3])  # meter
            reward = distance / (time.total_seconds() / 60)  # meter/second
            real_reward(forder, reward, q_setting)
    except Exception as e:
        logging.critical(e, exc_info=True)


def computeAction(agent, city, q_setting):
    try:
        state = computeState(agent, city)
        exp_exp_tradeoff = random.uniform(0, 1)
        if exp_exp_tradeoff > q_setting[0][8] and q_setting[0][3][state][0] != q_setting[0][3][state][1]:
            return 0 if q_setting[0][3][state][0] > q_setting[0][3][state][1] else 1
        else:
            return random.randint(0, 1)
    except Exception as e:
        logging.critical(e, exc_info=True)


def computeState(agent, city):
    try:
        state = [int(abs(float(city[2]) - float(city[4]) - float(agent[4])) / (
                float(city[4]) * 2 / 50)),
                 int(abs(float(city[3]) - float(city[4]) - float(agent[3])) / (
                         float(city[4]) * 2 / 50))]
        state = state[0] * 50 + state[1]
        if state < 0:
            return 0
        elif state > 2499:
            return 2499
        else:
            return state
    except Exception as e:
        logging.critical(e, exc_info=True)
