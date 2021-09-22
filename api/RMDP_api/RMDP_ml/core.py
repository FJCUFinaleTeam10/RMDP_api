import copy
import os
from datetime import datetime, timedelta
import itertools
import math
import logging
from concurrent.futures import ThreadPoolExecutor
from Database_Operator.Mongo_Operator import Mongo_Operate
from Math import Geometry

class RMDP:

    def __init__(self):
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True

        self.S = 0
        self.time_buffer = timedelta(minutes=0)
        self.t_Pmax = timedelta(seconds=40)
        self.t_ba = 10
        self.delay = 5
        self.capacity = 5
        self.velocity: float = 50 * 0.2777777777777778
        self.restaurantPrepareTime = timedelta(minutes=20)
        self.deadlineTime = timedelta(minutes=40)

        self.DBclient = Mongo_Operate()

        self.p = math.pi / 180

    def generateThread(self):
        cityList = self.DBclient.getAllCity()#get all city
        totalCurrentWorker = 2
        logging.info("start generating")
        with ThreadPoolExecutor(max_workers=totalCurrentWorker) as executor:
            threads = []
            for i in range(len(cityList)):
                threads.append(executor.submit(self.runRMDP, index=i, cityName=(cityList[i]['City'])))

    def runRMDP(self, index, cityName):
        try:
            delay = float("inf")
            slack = 0
            skipPostponement = False
            pairdOrder = []
            maxLengthPost = 5
            restaurantList = self.DBclient.getRestaurantListBaseOnCity(cityName)
            driverList = self.DBclient.getDriverBaseOnCity(cityName)
            filterrestTaurantCode = list(map(lambda x: int(x['Restaurant_ID']), restaurantList))# set all restaurant_id to int

            unAssignOrder = self.DBclient.getOrderBaseOnCity(filterrestTaurantCode, "unasgined")# get unassign order

            postponedOrder = self.DBclient.getOrderBaseOnCity(filterrestTaurantCode, "watting")# get postpone order

            S = 0
            if len(unAssignOrder) == 0 and len(postponedOrder) > 0:
                skipPostponement = True
                unAssignOrder = copy.deepcopy(postponedOrder)
                postponedOrder.clear()
            if maxLengthPost <= len(unAssignOrder):
                maxLengthPost = len(unAssignOrder) + 1

            for permutation in itertools.permutations(unAssignOrder):

                currentDriverList = copy.deepcopy(driverList)
                P_hat = copy.deepcopy(postponedOrder) #waitting order
                currentPairdOrder = copy.deepcopy(pairdOrder)
                for D in permutation:
                    currentPairdRestaurent = next(restaurant for restaurant in restaurantList if
                                                  restaurant['Restaurant_ID'] == D[
                                                      "order_restaurant_carrier_restaurantId"])
                    currentPairdDriverId = self.FindVehicle(D, currentPairdRestaurent, currentDriverList)
                    D["driver_id"] = currentDriverList[currentPairdDriverId]['Driver_ID']
                    currentDriverList[currentPairdDriverId]['Capacity'] += 1 #why assign twice
                    currentDriverList[currentPairdDriverId]['Route'] = copy.deepcopy(
                        self.AssignOrder(D, currentDriverList[currentPairdDriverId], currentPairdRestaurent))

                    if skipPostponement:
                        currentPairdOrder.append(D)
                    else:
                        if self.Postponement(P_hat, D, maxLengthPost):
                            P_hat.append(D)
                        else:
                            while (D['order_request_time'] - P_hat[0]['order_request_time']) >= self.t_Pmax:
                                PairedRestaurent = copy.deepcopy(next(restaurant for restaurant in restaurantList if
                                                                      restaurant['Restaurant_ID'] == P_hat[0][
                                                                          "order_restaurant_carrier_restaurantId"]
                                                                      ))
                                PairdDriverId = self.FindVehicle(P_hat[0], PairedRestaurent, driverList)
                                P_hat[0]['driver_id'] = str(currentDriverList[PairdDriverId]['Driver_ID'])
                                driverList[PairdDriverId]['Capacity'] += 1
                                driverList[PairdDriverId]['Route'] = copy.deepcopy(
                                    self.AssignOrder(P_hat[0], currentDriverList[PairdDriverId], PairedRestaurent))
                                pairdOrder.append(P_hat[0])#add finish order
                                P_hat.pop(0)
                                if len(P_hat) == 0:
                                    break
                            if len(P_hat) >= maxLengthPost:
                                for order in P_hat:
                                    PairedRestaurent = copy.deepcopy(next(
                                        restaurant for restaurant in restaurantList if
                                        int(restaurant['Restaurant_ID']) == int(
                                            order["order_restaurant_carrier_restaurantId"])))
                                    PairdDriverId = self.FindVehicle(order, PairedRestaurent,
                                                                     currentDriverList)
                                    currentDriverList[PairdDriverId]['Capacity'] += 1
                                    order['driver_id'] = str(currentDriverList[PairdDriverId]['Driver_ID'])
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
                currentPairedDriver = next(
                    driver for driver in driverList if str(driver['Driver_ID']) == str(order['driver_id']))
                currentPairedDriverId = driverList.index(
                    currentPairedDriver) if currentPairedDriver in driverList else -1
                driverList[currentPairedDriverId]['Route'] = copy.deepcopy(list(filter(
                    lambda x: (int(x['nodeType']) == 0 and x['Order_ID'] != order['Order_ID']) or (  #why no string
                            int(x['nodeType']) == 1 and str(x['Order_ID']) != str(order['Order_ID'])),
                    driverList[currentPairedDriverId]['Route'])))

            self.updateDriver(driverList)
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
        except Exception as e:
            logging.critical(e, exc_info=True)

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

    # main function

    def Slack(self, driverList):
        return sum(self.slackDelay(driver['Route'], driver['Latitude'], driver['Longitude']) for driver in driverList)

    def tripTime(self, driv, res, order):
        try:
            disDriver2Res = Geometry.coorDistance(float(driv['Latitude']), float(driv['Longitude']), #get distance d->r
                                                  float(res['Latitude']),
                                                  float(res['Longitude']))
            Res2Delivery = Geometry.coorDistance(float(res['Latitude']), float(res['Longitude']), #get distance r->o
                                                 float(order['Latitude']),
                                                 float(order['Longitude']))
            return float(disDriver2Res + Res2Delivery / float(self.velocity))# time
        except Exception as e:
            logging.critical(e, exc_info=True)

    def FindVehicle(self, Order, OrderRestaurant, driverList):
        try:
            handleDriver = list(filter(lambda driver: int(driver['Capacity']) < int(self.capacity), driverList))#get less than capacity driver
            distanceList = list(map(lambda x: self.tripTime(x, OrderRestaurant, Order), handleDriver))#getall triptime
            return distanceList.index(min(distanceList))# return min driver in index
        except Exception as e:
            logging.critical(e, exc_info=True)

    def slackDelay(self, route, Longitude, Latitude):
        try:
            delay: int = 0
            tripTime: int = 0
            currentRoute: list = copy.deepcopy(route)
            currentRoute.insert(0, {"Longitude": Longitude, "Latitude": Latitude, 'nodeType': 2})
            for i in range(1, len(currentRoute), 1):
                currentDistance = Geometry.coorDistance(float(currentRoute[i - 1]['Latitude']),
                                                        float(currentRoute[i - 1]['Longitude']),
                                                        float(currentRoute[i]['Latitude']),
                                                        float(currentRoute[i]['Longitude']))
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

    def Postponement(self, P_hat, D, maxLengthPost):
        try:
            if len(P_hat) < maxLengthPost or D['order_request_time'] - P_hat[0][
                'order_request_time'] < self.t_Pmax:  # if postponement set is empty
                return True
            else:
                return False
        except Exception as e:
            logging.critical(e, exc_info=True)

    def updateDriver(self, driverList):
        try:
            for driver in list(filter(lambda driver: len(driver['Route']) > 0, driverList)):
                driver['Velocity'] = self.velocity
                self.DBclient.updateDriver(driver)
        except Exception as e:
            logging.critical(e, exc_info=True)

    def updatePosponedOrder(self, pospondList):

        for order in pospondList:
            try:
                order['order_status'] = 'waiting'
                self.DBclient.updateOrder(order)
            except Exception as e:
                logging.critical(e, exc_info=True)

    def updatePairdOrder(self, pairedOrderList):
        try:
            for order in pairedOrderList:
                order['order_status'] = 'headToRes'
                order['order_approved_at'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                order['order_estimated_delivery_date'] = (datetime.now() + self.deadlineTime).strftime(
                    "%d-%m-%Y %H:%M:%S")
                self.DBclient.updateOrder(order)
        except Exception as e:
            logging.critical(e, exc_info=True)

    def Qing(self, Ds_0, restaurant, driverlist, city):
        # for episode in range(self.total_episodes):

        #for order in Ds_0:
        rest_pos = [float(restaurant['Latitude']), float(restaurant['Longitude'])]
        delivery_pos = np.array([float(Ds_0['Latitude']), float(Ds_0['Longitude'])])
        agents_dis = np.zeros((5, 1))  # 存距離
        agents_delay = np.zeros((5, 1))  # 存delay
        agents = []  # vehicle class
        counter = 0
        low_capacity = 5
        for v in driverList:
            v_delay = 0
            v_capacity = int(v['Capacity'])
            if v_capacity > low_capacity:
                continue
            elif v_capacity < low_capacity:
                low_capacity = v_capacity
                agents = []
                counter = 0
                agents_dis = np.zeros((5, 1))       #nearBY
                agents_delay = np.zeros((5, 1))
            vehicle_pos = [float(v['Latitude']),float(v['Longitude'])]
            dist = Geometry.coorDistance(vehicle_pos[0], vehicle_pos[1], rest_pos[0], rest_pos[1])
            if counter < 5:
                agents_dis[counter] = dist
                agents_delay[counter] = v_delay
                agents.append(v)
                counter += 1
            else:
                index = np.argmax(agents_delay)
                if agents_delay[index] > v_delay:
                    agents_delay[index] = v_delay
                    agents_dis[index] = dist
                    agents[index] = v
                elif agents_delay[index] == v_delay:
                    if agents_dis[index] > dist:
                        agents_delay[index] = v_delay
                        agents_dis[index] = dist
                        agents[index] = v
        action = 0
        agent = 0
        for agent in agents:
            agent_pos = np.array([agent['Latitude'],agent['Longitude']])
            cityList = self.DBclient.getAllCity()
            currentcity = copy.deepcopy(
                                        next(filter(lambda x: string(x['city']) == city, cityList),
                                             None))
            state = [abs(float(currentcity['Latitude']) - agent_pos[0]) / (currentcity['radius']*2 / 50),abs(float(currentcity['Longitude']) - agent_pos[1]) / (currentcity['radius']*2 / 50)]
            state = state[0] * 50 + state[1]
            # decide action
            exp_exp_tradeoff = random.uniform(0, 1)
            if exp_exp_tradeoff > 1.0:
                action = np.argmax(self.q_table[state, :])
            else:
                action = random.randint(0, 1)
            if action == 1:
                break
        # if all agent false take order
        if action == 0:
            agent = agents[random.randint(0, len(agents))]
            state = [abs(float(currentcity['Latitude']) - agent_pos[0]) / (currentcity['radius']*2 / 50),abs(float(currentcity['Longitude']) - agent_pos[1]) / (currentcity['radius']*2 / 50)]
            state = state[0] * 50 + state[1]
            action = 1

        # check if agent has order not finish yet
        self.driver_old_status = [] #len(drivierlist),[driverId,state,reward]
        agent_capacity = low_capacity
        agent_id = agent['Driver_ID']
        old_state = 0
        old_reward = 0
        old_state = 0
        order_id = 0
        agent_index = 0
        if agent_capacity > 0:
            for i in range(0,len(driverlist)):
                if driver_old_status[i][0] == agent_id:
                    agent_index = i
                    old_state = driver_old_status[i][1]
                    old_reward = driver_old_status[i][2]
                    self.q_table[old_state][1] = old_reward
                    driver_old_status[i][1] = state
                    driver_old_status[i][2] = self.q_table[state, 1]
                    break

        # Take the action with environment
        self.agent_orders_state = [] #len(driverList),np.array((5,2)) [driverid,np(5,2)],np(5,2)->[orderid,state]
        for i in range(0,len(driverlist)):
            if agent_orders_state[i][0] == agent_id:
                agent_order_list = agent_orders_state[i][1]
                for k in len(agent_order_list):
                    if agent_order_list[k][0] == 0:
                        agent_order_list[k][0] = Ds_0['Order_ID']
                        agent_order_list[k][1] = state
                        break


        new_state = [float(Ds_0['Latitude']),float(Ds_0['Longitude'])]
        reward =  Geometry.coorDistance(rest_pos[0], rest_pos[1], delivery_pos[0], delivery_pos[1])/ ((Geometry.coorDistance(rest_pos[0], rest_pos[1], delivery_pos[0], delivery_pos[1])/self.velocity)+self.restaurantPrepareTime)# (resturant to delivery distance)/(finish time)

        # update q_table
        self.q_table[state, action] = self.q_table[state,
                                                   action] + self.learning_rate * (
                                              reward + self.gamma * np.max(self.q_table[new_state, :]) -
                                              self.q_table[state, action])
        return agent_id
        '''
            # reduce episode
            episode = self.min_epsilon + \
                (self.max_epsilon-self.min_epsilon) * \
                np.exp(-self.decay_rate*episode)
            '''
        # reward = resturant&delivery distance / finish time

    def real_reward(self, agent_id, order_id, reward):
        self.agent_orders_state = []
        for i in len(vehicle_List):
            if agent_id == self.agent_orders_state[i][0]:
                agent_order = self.agent_orders_state[i][1]
                for k in len(agent_order):
                    if order_id == agent_order[0]:
                        state = agent_order[1]
                        self.q_table[state, 1] = reward
TEST = RMDP()
TEST.generateThread()
