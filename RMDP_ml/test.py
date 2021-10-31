import copy
import logging
import math
import os
import random
from datetime import datetime, timedelta, time
import numpy as np
from RMDP_ml.Math import Geometry
from RMDP_ml.Database_Operator import Mongo_Operator
import numba
import time
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

'''
def generateThread():
    cityList = Mongo_Operator.getAllCity()
    start = time.time()
    np.apply_along_axis(sequencePermutation, axis=1, arr=cityList)
    end = time.time()
    print(end - start)

def sequencePermutation(city):

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
        a = []
        restaurantList = Mongo_Operator.getRestaurantListBaseOnCity(city[0])
        driverList = Mongo_Operator.getDriverBaseOnCity(city[0])
        filterrestTaurantCode = restaurantList[:, 0].tolist()
        unAssignOrder = Mongo_Operator.getOrderBaseOnCity(filterrestTaurantCode, 0)  # get unassigned order
        q_setting = Mongo_Operator.getQlearning(city[0])
        #print(a)
        #nonUpdateOrder = np.vstack((order for order in unAssignOrder if order[7] == 0)) # finishorder[7]
        #n = unAssignOrder['order_request_time']
        print(q_setting[0][3][10][1])

        #print(q_setting)


generateThread()
'''




def Postponement(P_hat, D, maxLengthPost):
    if len(P_hat)==0:
        return True
    return True if len(P_hat) < maxLengthPost and D[9] - P_hat[0][9] < t_Pmax else False
P = []
D = []
max = 20
print(Postponement(P,D,max))