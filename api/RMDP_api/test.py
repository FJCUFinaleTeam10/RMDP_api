import copy
from datetime import datetime
import math
from RMDP_ml.userSimulator import userSimulator
from RMDP_ml.driverSimulator import driverSimulator
from RMDP_ml.new_core import SA
import json

#init
cityIndex = 67   #city index
restaurant_prepareTime = 10     #restaurant prepare meal time
velocity = 60           #agent velocity
capacity = 5            #agent carry orders maxium per sec
deadline = 40           #order's finish deadline
with open('QTable.json') as f:
    data = copy.deepcopy(json.load(f))
q_table = copy.deepcopy(data)

currentAssign = SA(cityIndex, restaurant_prepareTime, velocity, deadline, capacity, q_table)
currentGenerate = userSimulator(cityIndex, restaurant_prepareTime, velocity, deadline, capacity, q_table)
currentUpdate = driverSimulator(cityIndex, restaurant_prepareTime, velocity, deadline, capacity, q_table)
orders = []
drivers = currentGenerate.driverList

#init
start = datetime.now()
generateDataTime = 4    #per min
generateDataTime = math.floor(60/generateDataTime)
assigntime = generateDataTime*5
total_car = len(drivers)*5
currentAssign.total_car = total_car

for time_tik in range(0,13200):
    print(time_tik)
    if time_tik%generateDataTime == 0 and time_tik != 0 and time_tik <= 10800:
        print('generating data------------------------------------------------------------------------------------------')
        currentGenerate.generateThread(time_tik, orders, drivers)
    currentAssign.orderOnWay = currentUpdate.orderOnWay
    if time_tik % assigntime == 0 and time_tik != 0 and currentAssign.orderOnWay<total_car:
        print('assign order---------------------------------------------------------------------------------------------')
        currentAssign.generateThread(time_tik, orders, drivers)
        orders = copy.deepcopy(currentAssign.orders)
        drivers = copy.deepcopy(currentAssign.driverList)
        currentUpdate.orderOnWay=currentAssign.orderOnWay
    currentUpdate.generateThread(time_tik, orders, drivers)
    drivers = copy.deepcopy(currentUpdate.driverList)
    orders = copy.deepcopy(currentUpdate.orders)
currentUpdate.update()
end = datetime.now()

print(start)
print(end)
print(currentUpdate.onTime)
print(currentUpdate.outTime)




