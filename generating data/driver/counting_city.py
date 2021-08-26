#from change import Country_code

import pandas as pd
import pymongo
import random
import csv
import json
import pandas as pd
from pymongo import MongoClient

client = client = MongoClient('mongodb://localhost:27017/RMDP')
db = client["RMDP"]
testDriverCollection = db["driver"]
#data = pd.read_csv('zomato.csv',encoding = 'ISO-8859-1')
world_cities = pd.read_csv('all_cities.csv',encoding='ISO-8859-1')



Country_code = world_cities['Country_Code'].to_list()
City = world_cities['City'].to_list()
Longitude = world_cities['Longitude'].to_list()
Latitude = world_cities['Latitude'].to_list()
Radius = world_cities['radius'].to_list()

df = pd.DataFrame(columns=['Country_Code','City','Longitude','Latitude','Velocity','Capacity','Route'])

#print(driver_city)
'''

error_city = []
city_name = []
city_Longitude = []
city_Latitude = []
city_counter = 1
city_name.append(driver_city[0])
for i in range(1,len(driver_city)):
    if driver_city[i-1]!=driver_city[i]:
        city_counter+=1
        city_name.append(driver_city[i])
for i in range(0,len(city_name)):
    
    try:
        world_cities_name.index(city_name[i])
    except ValueError:
        error_city.append(city_name[i])
        city_Longitude.append('Null')
        city_Latitude.append('Null')
        continue
    
    if city_name[i] =='ÛÁstanbul':
        city_Latitude.append(41)
        city_Longitude.append(29)
        continue
    
    if city_name[i] == 'Sí£o Paulo':
        city_Latitude.append(-23.533773)
        city_Longitude.append(-46.62529)
        continue 
    c = world_cities_name.index(city_name[i])
    city_Longitude.append(world_cities_longitude[c])
    city_Latitude.append(world_cities_latitude[c])

print(city_name)
#print(city_Longitude[0])
print(error_city)

'''
#print(random.uniform(float(city_Longitude[0])-0.5,float(city_Longitude[0])+0.5))

#error_city_longitude = [30.193 ,26.27,30.679951,   20,28.535517,30.695202,17.686815]
#error_city_latitude =  [78.0246,80.14,76.722107,73.48,77.391029,76.854172,83.218483]

#df = pd.DataFrame(columns=['Country_Code','City','Longitude','Latitude'])
for i in range (0,len(City)):
    for j in range(0,30):
        new_row = {'Country_Code':Country_code[i],'City':City[i],'Longitude':random.uniform(float(Longitude[i])-float(Radius[i]),float(Longitude[i])+float(Radius[i])),'Latitude':random.uniform(float(Latitude[i])-float(Radius[i]),float(Latitude[i])+float(Radius[i])),'Velocity':0,'Capacity':0,'Route':[]}
        testDriverCollection.insert_one(new_row)


#data_json = json.loads(df.to_json(orient='records'))
#collection.insert_many(data_json)
#df.to_csv("driver1.csv",mode = 'a', header = False, index = False)

#India_city_longitude = [78.02,72.37,81.84,74.52,75.14,77.35,77.24,85.5 ,76.55,80.27,76.58,78.04,77.30,77.41,73.56,77.02,91.75,78.29,75.86,75.80,80.33,76.22,88.36,80.55,75.84,74.52,76.72,72.82,76.42,79.08]
#India_city_latitude =  [27.18,23.02,25.45,31.38,19.32,12.59,23.16,20.15,30.44,13.09,11.00,30.19,28.38,28.66,15.31,28.28,26.19,17.23,22.72,26.92,26.47,10.02,22.57,26.51,30.91,12.52,30.70,18.96,12.23,21.16]
