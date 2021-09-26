from Database_Operator.Mongo_Operator import Mongo_Operate
import random
T = Mongo_Operate()



a = "Agra"
c = T.getDriverBaseOnCity(a)
k = c[1]['Driver_ID']
v_index = next((index for (index, d) in enumerate(c) if d['Driver_ID'] == k), None)
ton_index = list((index for (index,d)in enumerate(c[v_index]['order_list']) if d[0] == 0),None)
print(ton_index)
'''
c[0]['order_list'][2][0] = 0
c[0]['order_list'][2][1] = 0
T.updateDriver(c[0])
'''
#print(c['q_table'][0][:])
#T.updateQlearning(c)

#print(random.randint(0,1))
'''
DriverList = T.getDriverBaseOnCity(a)
s = DriverList[1]['Driver_ID']
print(s)
for i in range (0,len(DriverList)):
    if DriverList[i]['Driver_ID'] == s:
        driverindex = i
print(driverindex)
'''