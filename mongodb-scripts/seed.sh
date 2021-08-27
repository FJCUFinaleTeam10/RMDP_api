#!/usr/bin/env bash

echo "start importing data"
# db_to_feed needs to be defined
# mongorestore -u mongoadmin -p mypass --authenticationDatabase admin -d db_to_feed ./mongo-seed-data
# e.g.
echo "data imported"
echo "Doing other useful mongodb database stuff, e.g creating additional mongo users..."
mongo admin -u mongoadmin -p mypass --eval "db.createUser({user: 'admin', pwd: 'admin', roles: [{role: 'readWrite', db: 'RMDP'}]});"
mongorestore -u admin -p admin --authenticationDatabase admin -d RMDP /data/mongo-seed-data
#echo "Mongo users created."

