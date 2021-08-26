import pandas as pd
import random
import csv
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
import time 
import datetime
client = MongoClient('mongodb://localhost:27017/RMDP')
db = client["RMDP"]
routingCollection = db["routing"]
data = pd.read_csv(r"C:\Users\Andychen\Desktop\routing\Delivery truck trip data.csv", encoding='ISO-8859-1')
data2 = pd.read_csv(r"C:\Users\Andychen\Desktop\routing\zomato.csv", encoding='ISO-8859-1')
data3 = pd.read_csv(r"C:\Users\Andychen\Desktop\routing\driver.csv", encoding='ISO-8859-1')
data4 = pd.read_csv(r"C:\Users\Andychen\Desktop\routing\order.csv", encoding='ISO-8859-1')

Order_Id = data4['_id'].tolist()
Order_Date = data['BookingID_Date'] .tolist()
Order_Time = data['Planned_ETA'].tolist()
#Order_Location = data['Destination_Location'].tolist()
#print(Order_Time)

Order_Longitude = -91.530167
Order_Latitude = 41.661129
radius = 0.037063067
data2 = data2[data2['City']=='Cedar Rapids/Iowa City']
data3 = data3[data3['City']=='Cedar Rapids/Iowa City']
Restaurant_Id = data2['Restaurant ID'].tolist()
Restaurant_Longitude = data2['Longitude'].tolist()
Restaurant_Latitude = data2['Latitude'].tolist()

driver_Id = data3['_id'].to_list()
df = pd.DataFrame(columns=['Order_Id','Order_Time','Order_Longitude','Order_Latitude','Driver_Id','Restaurant_Id','Restaurant_Longitude','Restaurant_Latitude'])
def strTimeProp(start,end,prop,frmt):
    stime = time.mktime(time.strptime(start,frmt))
    etime = time.mktime(time.strptime(end,frmt))
    ptime = stime + prop*(etime - stime)
    return int(ptime)
def randomDate(start,end,frmt='%Y-%m-%d %H:%M:%S'):
    return time.strftime(frmt,time.localtime(strTimeProp(start,end,random.random(),frmt)))

start = '2021-01-01 07:00:00'
end = '2021-01-01 23:59:59'
for i in range (0,len(Order_Date)):
    a = random.randint(0,len(Restaurant_Id)-1)
    b = i%len(driver_Id)
    c = random.randint(0,1)
    new_row = {'Order_Id':ObjectId(Order_Id[c]),'Order_Time':randomDate(start,end),'Order_Longitude':random.uniform(-91.530167-0.037063067,-91.530167+0.037063067),'Order_Latitude':random.uniform(41.661129-0.037063067,41.661129+0.037063067),'Driver_Id':ObjectId(driver_Id[b]),'Restaurant_Id':Restaurant_Id[a],'Restaurant_Longitude':Restaurant_Longitude[a],'Restaurant_Latitude':Restaurant_Latitude[a]}   
    routingCollection.insert_one(new_row)
    #df = df.append(new_row, ignore_index=True)

#df = json.loads(df.to_json(orient='records'))
#routingCollection.insert_many(df)
