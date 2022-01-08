import copy
import os
from datetime import datetime, timedelta

import logging
from concurrent.futures import ThreadPoolExecutor
from Database_Operator.Mongo_Operator import Mongo_Operate
from Math import Geometry
import numpy as np
import random
import time
import math
import itertools

class SA:
   def __init__(self, cityIndex, restaurant_prepareTime, velocity, deadline, capacity, q_table):
       self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
       # self.DEBUG = True
       # RMDP_setting
       #self.S = 0
       self.time_buffer = 0
       #self.t_Pmax = 40
       #self.t_ba = 10
       #self.delay = 5
       self.capacity = capacity
       self.velocity: float = velocity * 0.2777777777777778
       self.restaurantPrepareTime = restaurant_prepareTime*60
       self.deadlineTime = deadline*60
       self.DBclient = Mongo_Operate()
       self.p = math.pi / 180
       self.time_tik = 0
       self.cityList = self.DBclient.getAllCity()  # get all city
       self.cityIndex = cityIndex
       self.restaurantList = self.DBclient.getRestaurantListBaseOnCity(self.cityList[self.cityIndex]['City'])
       self.q_setting = self.DBclient.getQlearning(self.cityList[self.cityIndex]['City'])
       self.driverList = []
       self.orders = []
       self.orderOnWay = 0
       self.total_car = 0
       self.qtable = q_table


   def generateThread(self, time_tik, orders, driverList):
       self.time_tik = time_tik
       totalCurrentWorker = 1
       logging.info("start generating")
       with ThreadPoolExecutor(max_workers=totalCurrentWorker) as executor:
           threads = []
           self.orders = copy.deepcopy(orders)
           self.driverList = copy.deepcopy(driverList)
           threads.append(executor.submit(self.sequencePermutation, index=self.cityIndex, cityName=(self.cityList[self.cityIndex])))

   def sequencePermutation(self, index, cityName):
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
           delay = float("inf")
           slack = 0
           skipPostponement = False
           maxLengthPost = 0
           filterrestTaurantCode = list(
               map(lambda x: int(x['Restaurant_ID']), self.restaurantList))  # set all restaurant_id to int
           temp = self.DBclient.getOrderBaseOnCity(filterrestTaurantCode,
                                                            "unassigned")  # get unassigned order
           unAssignOrder = []
           ins = self.total_car-self.orderOnWay
           tr=False
           if ins != 0 and len(temp)>0:
               tr=True
           if ins > len(temp):
               ins = len(temp)
           elif ins < 0:
               ins = 0
           '''if ins > 5:
               ins = 5'''
           for i in range(0, ins):
               unAssignOrder.append(copy.deepcopy(temp[i]))
               self.orderOnWay += 1
           if tr:
               print(len(unAssignOrder))

           postponedOrder = 0

           S = 0
           # print(len(unAssignOrder))
           old_sequence = copy.deepcopy(unAssignOrder)
           delay_old, dr_list, paird_list, q_list = self.runRMDP(index, cityName, old_sequence,
                                                                            postponedOrder, self.driverList, self.restaurantList,
                                                                            pairdOrder, skipPostponement,
                                                                            maxLengthPost, self.q_setting)
           if ins < 7:
               ttt = copy.deepcopy(old_sequence)
               for new_sequence in itertools.permutations(ttt):
                   delay_new, driverList_new, pairdorder_new, q_setting_new = self.runRMDP(index,
                                                                                           cityName,
                                                                                           new_sequence,
                                                                                           postponedOrder,
                                                                                           self.driverList,self.restaurantList,pairdOrder,skipPostponement,maxLengthPost,self.q_setting)
                   if delay_new < delay_old:
                       old_sequence=copy.deepcopy(new_sequence)
                       delay_old = delay_new
                       dr_list = copy.deepcopy(driverList_new)
                       # post_list = copy.deepcopy(postponedOrder_new)
                       paird_list = copy.deepcopy(pairdorder_new)
                       q_list = copy.deepcopy(q_setting_new)
           else:
               start = time.time()
               end = 0
               # delay = 0

               while t > minT and len(old_sequence) > 1:
                   for _ in range(iterL):  # MonteCarlo method reject propblity

                       position_switch1 = 0
                       position_switch2 = random.randint(1, len(unAssignOrder) - 1)

                       new_sequence = copy.deepcopy(old_sequence)
                       new_sequence[position_switch1], new_sequence[position_switch2] = new_sequence[position_switch2], \
                                                                                        new_sequence[position_switch1]
                       # start = time.time()
                       delay_new, driverList_new, pairdorder_new, q_setting_new = self.runRMDP(index,
                                                                                                                   cityName,
                                                                                                                   new_sequence,
                                                                                                                   postponedOrder,
                                                                                                                   self.driverList,
                                                                                                                   self.restaurantList,
                                                                                                                   pairdOrder,
                                                                                                                   skipPostponement,
                                                                                                                   maxLengthPost,
                                                                                                                   self.q_setting)
                       # end  = time.time()
                       # print(end - start)
                       res = delay_new - delay_old
                       if res < 0 or math.exp(-res / (k * t)) > random.uniform(0, 1):
                           old_sequence = copy.deepcopy(new_sequence)
                           delay_old = delay_new
                           dr_list = copy.deepcopy(driverList_new)
                           #post_list = copy.deepcopy(postponedOrder_new)
                           paird_list = copy.deepcopy(pairdorder_new)
                           q_list = copy.deepcopy(q_setting_new)
                       counter += 1
                       end = time.time()
                       if end - start > 10:
                           # print(end - start)
                           break
                   if end - start > 10:
                       # print(end - start)
                       break
                   t = t * eta

           driverList = copy.deepcopy(dr_list)
           #postponedOrder = copy.deepcopy(post_list)
           pairdOrder = copy.deepcopy(paird_list)
           q_setting = copy.deepcopy(q_list)
           driverList = copy.deepcopy(self.updateDriver(driverList))
           pairdOrder = copy.deepcopy(self.updatePairdOrder(pairdOrder))
           for i in pairdOrder:
               self.orders.append(i)
           self.driverList = copy.deepcopy(driverList)
       except Exception as e:
           logging.critical(e, exc_info=True)

           # print("Thread:", index, " is finished")

   def runRMDP(self, index, cityName,unAssignOrder,postponedOrder,driverList,restaurantList,pairdOrder,skipPostponement,maxLengthPost,q_setting):
       try:
               #print('doing')
               currentDriverList = copy.deepcopy(driverList)
               currentPairdOrder = copy.deepcopy(pairdOrder)
               currentQ_setting = copy.deepcopy(q_setting)
               S = 0
               for D in unAssignOrder:
                   currentPairdRestaurent = next(restaurant for restaurant in restaurantList if
                                                 restaurant['Restaurant_ID'] == D[
                                                     "order_restaurant_carrier_restaurantId"])
                   #if skipPostponement:
                   currentPairdDriverId = self.FindVehicle(D,currentPairdRestaurent,currentDriverList,cityName)
                   D["driver_id"] = currentDriverList[currentPairdDriverId]['Driver_ID']
                   currentDriverList[currentPairdDriverId]['Capacity'] += 1  # why assign twice
                   currentDriverList[currentPairdDriverId]['Route'] = copy.deepcopy(
                       self.AssignOrder(D, currentDriverList[currentPairdDriverId], currentPairdRestaurent))
                   currentPairdOrder.append(D)
                   '''else:
                       if self.Postponement(P_hat, D, maxLengthPost):
                           P_hat.append(D)
                       else:
                           while (self.time_tik - P_hat[0]['order_request_time']) >= self.t_Pmax:
                               PairedRestaurent = copy.deepcopy(next(restaurant for restaurant in restaurantList if
                                                                     restaurant['Restaurant_ID'] == P_hat[0][
                                                                         "order_restaurant_carrier_restaurantId"]
                                                                     ))
                               PairdDriverId = self.FindVehicle(P_hat[0],currentPairdRestaurent,currentDriverList,cityName)
                               P_hat[0]['driver_id'] = str(currentDriverList[PairdDriverId]['Driver_ID'])
                               currentDriverList[PairdDriverId]['Capacity'] += 1
                               currentDriverList[PairdDriverId]['Route'] = copy.deepcopy(
                                   self.AssignOrder(P_hat[0], currentDriverList[PairdDriverId], PairedRestaurent))
                               currentDriverList[PairdDriverId]['Reward'] = Geometry.coorDistance(float(PairedRestaurent['Latitude']),
                                                       float(PairedRestaurent['Longitude']),
                                                       float(P_hat[0]['Latitude']), float(P_hat[0]['Longitude']))
                               currentPairdOrder.append(P_hat[0])  # add finish order
                               P_hat.pop(0)
                               if len(P_hat) == 0:
                                   break
                           if len(P_hat) >= maxLengthPost or self.time_tik == 10800:
                               for order in P_hat:
                                   PairedRestaurent = copy.deepcopy(next(
                                       restaurant for restaurant in restaurantList if
                                       int(restaurant['Restaurant_ID']) == int(
                                           order["order_restaurant_carrier_restaurantId"])))
                                   PairdDriverId = self.FindVehicle(order,currentPairdRestaurent,currentDriverList,cityName)
                                   currentDriverList[PairdDriverId]['Capacity'] += 1
                                   order['driver_id'] = str(currentDriverList[PairdDriverId]['Driver_ID'])
                                   currentDriverList[PairdDriverId]['Route'] = copy.deepcopy(
                                       self.AssignOrder(order, currentDriverList[PairdDriverId],
                                                        PairedRestaurent))
                                   currentDriverList[PairdDriverId]['Reward'] = Geometry.coorDistance(
                                       float(PairedRestaurent['Latitude']),
                                       float(PairedRestaurent['Longitude']),
                                       float(order['Latitude']), float(order['Longitude']))
                                   currentPairdOrder.append(order)
                               P_hat.clear()
                           P_hat.append(D)'''
               S = self.TotalDelay(currentDriverList)
               return S, currentDriverList, currentPairdOrder, currentQ_setting
               #return S,currentDriverList,P_hat,currentPairdOrder,currentQ_setting
       except Exception as e:
           logging.critical(e, exc_info=True)


   def deltaSDelay(self, route, Longitude, Latitude):
       try:
           delay: float = 0.0
           tripTime: float = self.time_tik
           currentRoute = copy.deepcopy(route)
           currentRoute.insert(0, {"Longitude": Longitude, "Latitude": Latitude, 'nodeType': 2})
           for i in range(1, len(currentRoute), 1):
               previousNode = currentRoute[i - 1]
               currentNode = currentRoute[i]
               currentDistance = Geometry.coorDistance(float(previousNode['Latitude']),
                                                       float(previousNode['Longitude']),
                                                       float(currentNode['Latitude']), float(currentNode['Longitude']))
               tripTime += currentDistance / (self.velocity/1000)
               if currentNode['nodeType'] == 0:
                   s = 0
                   for p in self.orders:
                       if p['Order_ID'] == currentNode['Order_ID']:
                           s = p['order_request_time']+self.restaurantPrepareTime
                           break
                   if s > self.time_tik:
                       tripTime+=(s-self.time_tik)
               elif 'order_request_time' in currentNode:
                   timeComplete = tripTime + self.time_buffer
                   # print(timeComplete)
                   # print(currentNode['order_request_time'])
                   timeDeadline = currentNode['order_request_time'] + self.deadlineTime
                   # print(timeDeadline)
                   timeDelay = timeComplete - timeDeadline
                   delay += max(0, timeDelay)
           return delay
       except Exception as e:
           logging.critical(e, exc_info=True)

   def AssignOrder(self, order, pairedDriver, currentParedRestaurent):
       try:
           #pair
           currentParedRestaurent['nodeType'] = 0
           currentParedRestaurent['Order_ID'] = order['Order_ID']
           order['nodeType'] = 1
           pairedDriver['Route'].append(currentParedRestaurent)
           pairedDriver['Route'].append(order)
           return pairedDriver['Route']
           #violent
           '''if len(pairedDriver['Route'])==0:
               currentParedRestaurent['nodeType'] = 0
               currentParedRestaurent['Order_ID'] = order['Order_ID']
               order['nodeType'] = 1
               pairedDriver['Route'].append(currentParedRestaurent)
               pairedDriver['Route'].append(order)
           else:
               totalRoute = copy.deepcopy(pairedDriver['Route'])
               currentParedRestaurent['nodeType'] = 0
               currentParedRestaurent['Order_ID'] = order['Order_ID']
               order['nodeType'] = 1
               totalRoute.append(currentParedRestaurent)
               totalRoute.append(order)
               a = len(totalRoute)
               first = copy.deepcopy(totalRoute[0])
               totalRoute.pop(0)

               orderList = []
               restList = []
               for i in totalRoute:
                   if i['nodeType'] == 0:
                       restList.append(copy.deepcopy(i))
                   else:
                       orderList.append(copy.deepcopy(i))
               now_route = []
               now_delay = float('inf')
               for rest in itertools.permutations(restList):
                   temp = copy.deepcopy(list(rest))
                   temp.insert(0,first)
                   temp_delay = float('inf')
                   start = 0
                   for orders in orderList:
                       for i in range(0,len(temp)):
                           if temp[i]['Order_ID']==orders['Order_ID']:
                               start = i
                               break
                       t = copy.deepcopy(temp)
                       t_delay = float('inf')
                       e = len(temp)+1
                       for i in range(start+1,e):
                           temp2 = copy.deepcopy(t)
                           temp2.insert(i,orders)
                           k = self.deltaSDelay(temp2, pairedDriver['Longitude'],pairedDriver['Latitude'])
                           if k < t_delay:
                               temp = copy.deepcopy(temp2)
                               t_delay = k
                       temp_delay = t_delay
                   if temp_delay < now_delay:
                       now_delay = temp_delay
                       now_route=copy.deepcopy(temp)
               if len(now_route) != a:
                   print('wrong')
               pairedDriver['Route'] = copy.deepcopy(now_route)
           return pairedDriver['Route']
           #insert'''
           #insertion method
           '''if not pairedDriver['Route']:
               pairedDriver['Route'].append(currentParedRestaurent)
               pairedDriver['Route'].append(order)
               pairedDriver['Route'][0]['nodeType'] = 0
               pairedDriver['Route'][0]['Order_ID'] = order['Order_ID']
               pairedDriver['Route'][1]['nodeType'] = 1
           else:
               first: int = 0
               second: int = 1
               minDelayTime = float('inf')
               currentParedRestaurent['nodeType'] = 0
               order['nodeType'] = 1
               currentParedRestaurent['Order_ID'] = order['Order_ID']
               for i in range(1, len(pairedDriver['Route']) + 1, 1):
                   for j in range(i + 1, len(pairedDriver['Route']) + 2, 1):
                       tmpDriver = copy.deepcopy(pairedDriver)
                       tmpDriver['Route'].insert(i, currentParedRestaurent)
                       tmpDriver['Route'].insert(j, order)
                       delayTime = self.deltaSDelay(tmpDriver['Route'], tmpDriver['Longitude'],
                                                    tmpDriver['Latitude'])
                       if minDelayTime > delayTime:
                           minDelayTime = delayTime
                           first = i
                           second = j
               pairedDriver['Route'].insert(first, currentParedRestaurent)
               pairedDriver['Route'][first]['nodeType'] = 0
               pairedDriver['Route'][first]['Order_ID'] = order['Order_ID']
               pairedDriver['Route'].insert(second, order)
               pairedDriver['Route'][second]['nodeType'] = 1
           return pairedDriver['Route']'''
       except Exception as e:
           logging.critical(e, exc_info=True)

   # main function

   def Slack(self, driverList):
       return sum(self.slackDelay(driver['Route'], driver['Latitude'], driver['Longitude']) for driver in driverList)

   def tripTime(self, driv, res, order):
       try:
           disDriver2Res = Geometry.coorDistance(float(driv['Latitude']), float(driv['Longitude']),
                                                 # get distance d->r
                                                 float(res['Latitude']),
                                                 float(res['Longitude']))
           Res2Delivery = Geometry.coorDistance(float(res['Latitude']), float(res['Longitude']),  # get distance r->o
                                                float(order['Latitude']),
                                                float(order['Longitude']))
           return float(disDriver2Res + Res2Delivery / float(self.velocity))  # time
       except Exception as e:
           logging.critical(e, exc_info=True)

   def FindVehicle(self, Order, OrderRestaurant, driverList, cityName):
       try:
           minCapacity = 5
           minDelay = float('inf')
           temp = list(filter(lambda driver: int(driver['Capacity']) < minCapacity,
                                      driverList))  # get less than capacity driver
           handleDriver = []
           for driver in temp:
               #t = copy.deepcopy(driver)
               #predict = self.AssignOrder(Order, t, OrderRestaurant)
               k = self.deltaSDelay(driver['Route'], driver['Longitude'], driver['Latitude'])
               if k < minDelay:
                   handleDriver = []
                   handleDriver.append(driver)
                   minDelay = k
               elif k == minDelay:
                   handleDriver.append(driver)
           #q-table
           '''stateList = list(map(lambda agent: self.computeState(agent, cityName), handleDriver))
           stateRes = self.compu(OrderRestaurant, cityName)
           arround_eight = []
           arround_sixteen = []
           finSix = False
           finEig = False
           for i in range(0,5):
               for j in range(0,5):
                   a = stateRes[0]
                   b = stateRes[1]
                   if i == 1:
                       a-=1
                   elif i == 2:
                       a+=1
                   elif i == 3:
                       a-=2
                   elif i == 4:
                       a+=2
                   if j == 1:
                       b -=1
                   elif j == 2:
                       b+=1
                   elif j == 3:
                       b-=2
                   elif j == 4:
                       b+=2
                   if (i >=3 or j >= 3) and (a*50+b in stateList):
                       arround_sixteen.append(a * 50 + b)
                       finSix = True
                   elif a*50+b in stateList:
                       arround_eight.append((a * 50 + b))
                       finEig = True
           return_agent_list = []
           now_reward = -1
           if finEig:
               for i in range(0, len(stateList)):
                   if stateList[i] in arround_eight and self.qtable[stateList[i]][1] > now_reward:
                       return_agent_list = []
                       return_agent_list.append(handleDriver[i])
                       now_reward = self.qtable[stateList[i]][1]
                   elif stateList[i] in arround_eight and self.qtable[stateList[i]][1] == now_reward:
                       return_agent_list.append(handleDriver[i])
           elif finSix:
               for i in range(0, len(stateList)):
                   if stateList[i] in arround_sixteen and self.qtable[stateList[i]][1] > now_reward:
                       return_agent_list = []
                       return_agent_list.append(handleDriver[i])
                       now_reward = self.qtable[stateList[i]][1]
                   elif stateList[i] in arround_sixteen and self.qtable[stateList[i]][1] == now_reward:
                       return_agent_list.append(handleDriver[i])
           else:
               for i in range(0, len(stateList)):
                   if self.qtable[stateList[i]][1] > now_reward:
                       return_agent_list = []
                       return_agent_list.append(handleDriver[i])
                       now_reward = self.qtable[stateList[i]][1]
                   elif self.qtable[stateList[i]][1] == now_reward:
                       return_agent_list.append(handleDriver[i])
           random.shuffle(return_agent_list)
           return driverList.index(return_agent_list[0])
           #distance'''
           minDistance = float('inf')
           distanceList = []
           for driver in handleDriver:
                if Geometry.coorDistance(driver['Latitude'], driver['Longitude'], OrderRestaurant['Latitude'], OrderRestaurant['Longitude']) < minDistance:
                    distanceList = []
                    minDistance = Geometry.coorDistance(driver['Latitude'], driver['Longitude'], OrderRestaurant['Latitude'], OrderRestaurant['Longitude'])
                    distanceList.append(driver)
                elif Geometry.coorDistance(driver['Latitude'], driver['Longitude'], OrderRestaurant['Latitude'], OrderRestaurant['Longitude']) == minDistance:
                    distanceList.append(driver)
           random.shuffle(distanceList)
           return driverList.index(distanceList[0])  # return min driver in index'''
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
           if len(P_hat) < maxLengthPost or len(P_hat)==0:  # if postponement set is empty
               return True
           else:
               return False
       except Exception as e:
           logging.critical(e, exc_info=True)

   def updateDriver(self, driverList):
       try:
           for driver in list(filter(lambda driver: len(driver['Route']) > 0, driverList)):
               driver['Velocity'] = self.velocity
           return driverList
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
               order['order_approved_at'] = self.time_tik
               order['order_estimated_delivery_date'] = order['order_request_time'] + self.deadlineTime
               self.DBclient.updateOrder(order)
           return pairedOrderList
       except Exception as e:
           logging.critical(e, exc_info=True)



   def Qing(self, Ds_0, restaurant, drlist, city, q_setting):
       # for episode in range(self.total_episodes):
       # for order in Ds_0:
       try:
           action = 0
           agent = 0
           low_capacity = min(driver['Capacity'] for driver in drlist)
           if low_capacity < self.capacity:
               filteredDriver = list(filter(lambda driver: driver['Capacity'] < 5, drlist))

               for v in filteredDriver:
                   t = copy.deepcopy(v)
                   predict = self.AssignOrder(Ds_0, t, restaurant)
                   v['delay'] = self.deltaSDelay(predict, v['Longitude'], v['Latitude'])
                   v['dist'] = Geometry.coorDistance(v['Latitude'], v['Longitude'], float(restaurant['Latitude']),
                                                     float(restaurant['Longitude']))
               filteredDriver = sorted(filteredDriver, key=lambda driver: (driver['delay'], driver['dist']))
               agents = filteredDriver[:] if len(filteredDriver) <= 5 else filteredDriver[0:5]

               selectedAgent = next((agent for agent in agents if self.computeAction(agent, city, q_setting) == 1),
                                    agents[0])
               action = 1
               state = self.computeState(selectedAgent, city)
               # check if agent has order not finish yet
               # self.driver_old_status = [] #len(drivierlist),[driverId,state,reward]
               return_index = next((index for (index, d) in enumerate(drlist) if d['Driver_ID'] == selectedAgent['Driver_ID']), None)
               #if low_capacity > 0:
               if selectedAgent['Capacity'] >0:
                   old_state = drlist[return_index]['State']
                   old_reward = drlist[return_index]['Reward']
                   q_setting['q_table'][old_state][1] = old_reward  # state write back to qtable
                   drlist[return_index]['State'] = state  # get new state status
                   drlist[return_index]['Reward'] = q_setting['q_table'][state][1]  # current state old reward

               Ds_0['Qtable_position'] = state

               new_state = self.computeState(Ds_0, city)
               res2orderDist = Geometry.coorDistance(float(restaurant['Latitude']), float(restaurant['Longitude']),
                                                     float(Ds_0['Latitude']), float(Ds_0['Longitude']))
               dri2ResDist = Geometry.coorDistance(float(selectedAgent['Latitude']), float(selectedAgent['Longitude']), float(restaurant['Latitude']), float(restaurant['Longitude']))
               res2orderDistTime = (res2orderDist+dri2ResDist) / (self.velocity/1000)
               reward = res2orderDist / res2orderDistTime
               # update q_table
               # print(new_state)

               max = q_setting['q_table'][new_state][1]
               q_setting['q_table'][new_state][0] = max
               q_setting['q_table'][state][action] = q_setting['q_table'][state][action] \
                                                     + q_setting['learning_rate'] * (
                                                             reward + q_setting['gamma'] * max -
                                                             q_setting['q_table'][state][action])
               q_setting['episode'] += 1
               q_setting['epsilon'] = q_setting['min_epislon'] + (
                       q_setting['max_epislon'] - q_setting['min_epislon']) * math.exp(
                   -q_setting['decay_rate'] * q_setting['episode'])
               return return_index,q_setting,Ds_0,drlist
       except Exception as e:
           logging.critical(e, exc_info=True)

   def real_reward(self, order, reward, q_setting):
       try:
           self.q_setting['q_table'][order['Qtable_position']][1] = q_setting['q_table'][order['Qtable_position']][1] + q_setting['learning_rate'] * (reward + q_setting['gamma'] * q_setting['q_table'][order['Qtable_position']][0]-q_setting['q_table'][order['Qtable_position']][1])

       except Exception as e:
           logging.critical(e, exc_info=True)

   def updateRealReward(self, finishOrder, restaurantList, q_setting):
       try:
           for forder in finishOrder:
               getrestaurant = next(
                   restaurant for restaurant in restaurantList if int(restaurant['Restaurant_ID']) == int(
                       forder["order_restaurant_carrier_restaurantId"]))
               time = forder['order_delivered_customer_date'] - forder['order_request_time']
               distance = Geometry.coorDistance(getrestaurant['Latitude'], getrestaurant['Longitude'],
                                                forder['Latitude'], forder['Longitude'])  # meter
               reward = distance / time  # meter/second
               self.real_reward(forder, reward, q_setting)
       except Exception as e:
           logging.critical(e, exc_info=True)

   def computeAction(self, agent, city, q_setting):

       state = self.computeState(agent, city)
       # decide action
       exp_exp_tradeoff = random.uniform(0, 1)

       # action = np.argmax(q_setting['q_table'][state, :])
       if exp_exp_tradeoff > q_setting['epsilon'] and q_setting['q_table'][state][0] != q_setting['q_table'][state][1]:
           return 0 if q_setting['q_table'][state][0] > q_setting['q_table'][state][1] else 1
       else:
           return random.randint(0, 1)
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
#TEST = SA()
#TEST.generateThread()