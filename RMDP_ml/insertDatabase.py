import csv
import json
import os

import pandas as pd
import pymongo
import numpy as np
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps.settings")
client = pymongo.MongoClient('mongodb://admin:admin@localhost:27017/RMDP?authSource=admin')
db = client ["RMDP"]
collection = db ["q_learning"]

#data = pd.read_json("new_driver.json")
world_city = pd.read_csv('all_cities.csv',encoding = 'ISO-8859-1')
City = world_city['City'].tolist()
City_id = world_city['City_id'].tolist()
Latitude = world_city['Latitude'].tolist()
Longitude = world_city['Longitude'].tolist()
slide_length = world_city['radius'].tolist()
df = pd.DataFrame(columns=['City','City_id','state_index','action_index','q_table', 'center', 'side_length', 'learning_rate', 'gamma', 'epsilon',
               'max_epislon', 'min_epislon', 'decay_rate', 'nearBY','capacity'])
for i in range(0,len(City)):
    new_row = {'City':City[i],'City_id':City_id[i],'state_index': 2500,'action_index': 2,'q_table':np.zeros(shape=(2500,2),dtype=float),'center':[Latitude[i],Longitude[i]],'slide_length': slide_length[i],
    'learning_rate': 0.8,
    'gamma': 0.95,
    'epsilon': 1,
    'max_epislon': 1,
    'min_epislon': 0.01,
    'decay_rate': 0.005,
    'nearBY': 5,
    'capacity': 5,
    'episode': 0}
    #collection.insert_one(new_row)
    df = df.append(new_row, ignore_index=True)
    data_json = json.loads(df.to_json(orient='records'))
collection.insert_many(data_json)




