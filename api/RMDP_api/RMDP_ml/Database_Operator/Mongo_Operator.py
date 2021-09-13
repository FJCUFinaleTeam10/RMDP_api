import os


class Mongo_Operate:
    def __init__(self):
        self.DEBUG = False if int(os.environ['DEBUG']) == 1 else True
        self.client = self.getMongoClientUrl(self.DEBUG)
        self.databaseName = self.client["RMDP"]
        self.restaurantCollection = self.databaseName["restaurant"]
        self.driverCollection = self.databaseName["driver"]
        self.all_citiesCollection = self.databaseName["all_cities"]
        self.country_codeCollection = self.databaseName["country_code"]
        self.orderCollection = self.databaseName["order"]

    def getMongoClientUrl(self, DEBUG):
        if DEBUG:
            return "mongodb://admin:admin@localhost:27017/RMDP?authSource=admin"
        else:
            return "mongodb://admin:admin@mongodb:27017/RMDP?authSource=admin"

    def getAllCity(self):
        return list(self.all_citiesCollection.find())

    def getDriverBaseOnCity(self, cityName):

        return list(Mongo_Operate.driverCollection.find({"City": cityName}))

