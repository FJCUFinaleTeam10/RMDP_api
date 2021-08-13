import copy
# from generatingData import generateTestData
# from Math.Geometry import interSectionCircleAndLine
from datetime import datetime, timedelta, date

from DistUpgrade.QUrlOpener import singleton
from django.forms.models import model_to_dict
import itertools
import math
import json
from driver.models import driver
from order.models import order
from restaurant.models import restaurant


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


@singleton
class RMDP:
    _instance = None

    def __init__(self, delay: int, maxLengthPost: int, maxTimePost: int,
                 capacity: int, velocity: int, restaurantPrepareTime: int, deadlineTime):

        self.D_0 = []  # Order
        self.Order_num = 2
        self.Delta_S = 0
        self.time_buffer = 0
        self.t_Pmax = 40
        self.t_ba = 10
        self.delay = delay
        self.maxLengthPost = maxLengthPost
        self.maxTimePost = maxTimePost
        self.capacity = capacity
        self.velocity: float = velocity * 0.2777777777777778
        self.restaurantPrepareTime = restaurantPrepareTime
        self.deadlineTime = deadlineTime
        self.Theta_x = []
        self.P_x = []

    def runRMDP(self, unAssignOrder: list):
        try:
            self.restaurantlist = list(restaurant.objects.all())
            self.vehicleList = list(driver.objects.all())

            delay: float = float("inf")
            slack = 0

            unassignedOrderPermutation = list(itertools.permutations(unAssignOrder))
            for permutation in unassignedOrderPermutation:
                Theta_hat = copy.deepcopy(self.vehicleList)  # Candidate route plan
                P_hat = memcacheDb.get('P_hat')

                if P_hat is None:
                    P_hat = []

                for D in permutation:

                    currentPairdDriver = self.FindVehicle(D)
                    D["driverId"] = (str(currentPairdDriver.id))
                    currentPairdRestaurentList = list(
                        filter(lambda x: str(x.id) == D["restaurantId"], self.restaurantlist))
                    currentPairdRestaurent = currentPairdRestaurentList[0].to_mongo().to_dict()

                    currentPairdRestaurent['orderId'] = str(D['orderId'])
                    currentPairdDriver.capacity += 1
                    Theta_hat = self.AssignOrder(Theta_hat, D, currentPairdDriver, currentPairdRestaurent)
                    if self.Postponement(P_hat, D, self.maxLengthPost, self.t_Pmax):
                        if D not in P_hat:
                            P_hat.append(D)
                    else:
                        while (D.t - P_hat[0].t) >= self.t_Pmax:
                            PairdDriver = self.FindVehicle(P_hat[0])
                            P_hat[0].setDriverId(PairdDriver.get_id())
                            PairdDriver.setCurrentCapacity(PairdDriver.getCurrentCapacity() + 1)
                            PairedRestaurent = copy.deepcopy(self.restaurantList[P_hat[0].getRestaurantId() - 1])
                            PairedRestaurent.setOrderId(D.getId())

                            self.AssignOrder(Theta_hat, P_hat[0], PairdDriver, PairedRestaurent)

                            P_hat.pop(0)
                            if len(P_hat) == 0:
                                break

                        if len(P_hat) >= self.maxLengthPost:
                            for pospondedOrder in P_hat:
                                PairdDriver = self.FindVehicle(pospondedOrder)
                                PairdDriver.setCurrentCapacity(PairdDriver.getCurrentCapacity() + 1)
                                pospondedOrder.setDriverId(PairdDriver.get_id())
                                PairedRestaurent = copy.deepcopy(
                                    self.restaurantList[pospondedOrder.getRestaurantId() - 1])
                                PairedRestaurent.setOrderId(pospondedOrder.getId())
                                self.AssignOrder(Theta_hat, pospondedOrder, PairdDriver, PairedRestaurent)
                            P_hat.clear()
                        P_hat.append(D)
                S = self.TotalDelay(Theta_hat)
                currentSlack = self.Slack(Theta_hat)
                if (S < delay) or ((S == delay) and (currentSlack < slack)):
                    slack = currentSlack
                    delay = S
                    self.Theta_x = copy.deepcopy(Theta_hat)
                    self.P_x = copy.deepcopy(P_hat)
            print(self.Theta_x)
            print(self.P_x)
            self.Remove()
            self.updateValue()
        except ValueError:
            print(ValueError)

    def deltaSDelay(self, driver):
        try:
            delay: float = 0.0
            tripTime: float = 0.0
            currentDriverLocation = {'longitude': driver['longitude'],
                                     'latitude': driver['latitude']}
            currentDriver = copy.deepcopy(driver)
            currentDriver.route.insert(0, currentDriverLocation)
            for i in range(1, len(currentDriver['route']), 1):
                previousNode = currentDriver['route'][i - 1]
                currentNode = currentDriver['route'][i]
                currentDistance = self.distance(float(previousNode['latitude']), float(previousNode['longitude']),
                                                float(currentNode['latitude']), float(currentNode['longitude']))
                tripTime += currentDistance / self.velocity
                if 'restaurantId' in currentNode:
                    deadlineTime = self.deadlineTime
                    timeComplete = timedelta(seconds=tripTime) + timedelta(
                        minutes=self.time_buffer) + datetime.now() + timedelta(hours=8)
                    timeDeadline = datetime.strptime(currentNode['requestTime'], "%d-%m-%Y %H:%M:%S") + timedelta(
                        minutes=deadlineTime)
                    timeDelay = timeDeadline - timeComplete
                    delay = max(0, timeDelay.days + timeDelay.total_seconds())
            return delay
        except ValueError:
            print(ValueError)

    def AssignOrder(self, Theta_hat, order, pairedDriver, currentParedRestaurent):
        currentDriver: list = next((driver for driver in Theta_hat if driver.id == pairedDriver.id), [])

        if not currentDriver.route:
            currentDriver.route.append(currentParedRestaurent)
            currentDriver.route.append(order)

        else:
            first: int = 0
            second: int = 1
            minDelayTime = float('inf')
            for i in range(0, len(currentDriver.route), 1):  # control Restaurant
                for j in range(i + 1, len(currentDriver.route) + 2, 1):  # find all the possible positioins of new order

                    tmpDriver = copy.deepcopy(currentDriver)
                    tmpDriver.route.insert(i, currentParedRestaurent)
                    tmpDriver.route.insert(j, order)
                    delayTime = self.deltaSDelay(tmpDriver)

                    if minDelayTime > delayTime:
                        minDelayTime = delayTime
                        first = i
                        second = j

            currentDriver.route.insert(first, currentParedRestaurent)
            currentDriver.route.insert(second, order)
        return Theta_hat

    # main function

    def Slack(self, Theta_hat):
        totalSlack: int = 0
        for routePerVehicle in Theta_hat:
            totalSlack += self.slackDelay(routePerVehicle)
        return totalSlack

    # def showPosition(self):
    #     plt.scatter(self.x_R, self.y_R, c='red', s=25)
    #     plt.scatter(self.x_V, self.y_V, c='green', s=25)
    #     plt.show()

    # def updateDriverLocation(self, time):
    #     hasOrderVehicle: list = [routePerVehicle for routePerVehicle in self.Theta_x if
    #                              (routePerVehicle['route'] != [])]
    #     for route in hasOrderVehicle:
    #         currentDriver: driver = self.vehiceList[route.get("driverId") - 1]
    #         targetDestination = route['route'][0]
    #         travledDistance = currentDriver.getVelocity() * time
    #         estimatedDistance = distance(currentDriver.getLatitude(),
    #                                      currentDriver.getLongitude(),
    #                                      targetDestination.getLatitude(),
    #                                      targetDestination.getLongitude())
    #         if travledDistance > 0:
    #
    #             if travledDistance >= estimatedDistance:
    #                 currentDriver.setLatitude(targetDestination.getLatitude())
    #                 currentDriver.setLongitude(targetDestination.getLongitude())
    #                 route['route'].pop(0)
    #             else:
    #                 updatedLon, updatedLat = interSectionCircleAndLine(currentDriver.getLongitude(),
    #                                                                    currentDriver.getLatitude(),
    #                                                                    travledDistance,
    #                                                                    currentDriver.getLongitude(),
    #                                                                    currentDriver.getLatitude(),
    #                                                                    targetDestination.getLongitude(),
    #                                                                    targetDestination.getLatitude())
    #                 currentDriver.setLatitude(updatedLon)
    #                 currentDriver.setLongitude(updatedLat)

    def tripTime(self, driv, res, order):
        disDriver2Res = self.distance(float(driv.latitude), float(driv.longitude), float(res.latitude),
                                      float(res.longitude))
        Res2Delivery = self.distance(float(res.latitude), float(res.longitude), float(order['latitude']),
                                     float(order['longitude']))
        return (disDriver2Res + Res2Delivery) / float(self.velocity)

    def FindVehicle(self, Order):
        OrderRestaurantList = list(filter(lambda x: str(x.id) == str(Order['restaurantId']), self.restaurantlist))
        OrderRestaurant = OrderRestaurantList[0]
        minTimeDriver = self.vehicleList[0]
        minTimeTolTal = float('inf')
        handleDriver = [driver for driver in self.vehicleList if driver.capacity < self.capacity]
        for currentDriver in handleDriver:
            currenTripTime = self.tripTime(currentDriver, OrderRestaurant, Order)
            if currenTripTime < minTimeTolTal:
                minTimeDriver = copy.deepcopy(currentDriver)
                minTimeTolTal = currenTripTime
        return minTimeDriver

    def slackDelay(self, driver):
        try:
            delay: int = 0
            tripTime: int = 0
            currentRoute: list = copy.deepcopy(driver['route'])
            currentRoute.append(driver)
            for i in range(1, len(currentRoute), 1):
                currentDistance = self.distance(float(currentRoute[i - 1]['latitude']),
                                                float(currentRoute[i - 1]['longitude']),
                                                float(currentRoute[i]['latitude']), float(currentRoute[i]['longitude']))
                tripTime += currentDistance / self.velocity
                if 'restaurantId' in currentRoute[i]:
                    deadLine = datetime.strptime(currentRoute[i]['deadLineTime'],
                                                 "%d-%m-%Y %H:%M:%S") - datetime.now() + timedelta(hours=8)
                    delay = timedelta(seconds=tripTime) - timedelta(seconds=self.time_buffer) - deadLine
                    delay = max(0, delay.total_seconds())
            return delay
        except ValueError:
            print(ValueError)

    def TotalDelay(self, theta_Hat: list):
        totalSlack: int = 0
        for routePerVehicle in theta_Hat:
            totalSlack += self.deltaSDelay(routePerVehicle)
        return totalSlack

    def Remove(self):
        for pospondedOrder in self.P_x:
            currentPairedDriverList = list(filter(lambda x: str(x.id) == str(pospondedOrder['driverId']), self.Theta_x))
            currentPairedDriver = currentPairedDriverList[0]
            targetRoute: list = next(
                (driver for driver in self.Theta_x if str(driver.id) == str(currentPairedDriver.id)), [])

            ans = list(filter(lambda x: (('restaurantId' in x) and
                                         str(x['orderId']) != str(pospondedOrder['orderId'])) or (
                                                ('requestTime' not in x) and ('route' not in x) and str(x['orderId']) !=
                                                str(pospondedOrder['orderId'])), targetRoute['route']))
            targetRoute['route'] = copy.deepcopy(ans[:])

    def Postponement(self, P_hat, D, p_max, t_Pmax):
        if len(P_hat) == 0:  # if postponement set is empty
            return True
        elif len(P_hat) < self.maxLengthPost:  # if number of postponement <= max of postponement
            if D.t - P_hat[0].t < t_Pmax:
                return True
            else:
                return False
        else:
            return False

    def distance(self, lat1, lon1, lat2, lon2):
        p = math.pi / 180
        a = 0.5 - math.cos((lat2 - lat1) * p) / 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (
                1 - math.cos((lon2 - lon1) * p)) / 2
        return 12742 * math.asin(math.sqrt(a))  # 2*R*asin...

    def updateValue(self):
        try:
            updateDriver = list(filter(lambda x: len(x['route']) > 0, self.Theta_x))
            for pairdDriver in updateDriver:
                currentObject = pairdDriver.to_mongo().to_dict()
                driver.objects(id=pairdDriver.id).update(
                    capacity=currentObject['capacity'],
                    route=currentObject['route'],
                    velocity=currentObject['velocity']
                )
            memcacheDb.hmset('P_hat', self.P_x)
        except ValueError:
            print((ValueError))
