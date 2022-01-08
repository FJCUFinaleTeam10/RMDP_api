import copy
import time
import math
from datetime import datetime

from RMDP_ml.userSimulator import userSimulator
from RMDP_ml.driverSimulator import driverSimulator
from RMDP_ml.new_core import SA
import csv

#init
cityIndex = 67
restaurant_prepareTime = 10
velocity = 60
capacity = 5
deadline = 40
with open('QTable.json') as f:
    data = copy.deepcopy(json.load(f))
q_table = copy.deepcopy(data)

currentAssign = SA(cityIndex, restaurant_prepareTime, velocity, deadline, capacity, q_table)
currentGenerate = userSimulator(cityIndex, restaurant_prepareTime, velocity, deadline, capacity, q_table)
currentUpdate = driverSimulator(cityIndex, restaurant_prepareTime, velocity, deadline, capacity, q_table)

start = datetime.now()
generateDataTime = 3    #per min
generateDataTime = math.floor(60/generateDataTime)
for time_tik in range(0,10801):
    print(time_tik)
    if time_tik%generateDataTime == 0 and time_tik != 0:
        currentGenerate.generateThread(time_tik, orders, drivers)