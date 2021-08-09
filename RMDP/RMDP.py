import copy
# from generatingData import generateTestData
# from Math.Geometry import interSectionCircleAndLine
from django.forms.models import model_to_dict
import itertools
import math
import json

from driver.models import driver
from order.models import order
from restaurant.models import restaurant


class RMDP:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        # singleton

    def __init__(self, delay: int, maxLengthPost: int, maxTimePost: int,
                 capacity: int, velocity: int, restaurantPrepareTime: int):

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
        self.velocity = velocity
        self.restaurantPrepareTime = restaurantPrepareTime

    def runRMDP(self, unAssignOrder: list):
        try:
            self.restaurantlist = list(restaurant.objects.all())
            self.vehicleList = list(driver.objects.all())

            P_x = []
            delay: float = float("inf")
            slack = 0

            unassignedOrderPermutation = list(itertools.permutations(unAssignOrder))
            for permutation in unassignedOrderPermutation:
                Theta_hat = copy.deepcopy(self.vehicleList)  # Candidate route plan
                P_hat = copy.deepcopy(P_x)

                for D in permutation:

                    currentPairdDriver = self.FindVehicle(D)
                    D["driverId"] = (str(currentPairdDriver.id))
                    currentPairdRestaurentList = list(filter(lambda x: str(x.id) == D["restaurantId"], self.restaurantlist))
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
                                PairedRestaurent = copy.deepcopy(self.restaurantList[pospondedOrder.getRestaurantId() - 1])
                                PairedRestaurent.setOrderId(pospondedOrder.getId())
                                self.AssignOrder(Theta_hat, pospondedOrder, PairdDriver, PairedRestaurent)
                            P_hat.clear()
                        P_hat.append(D)
                S = self.TotalDelay()
                if (S < delay) or ((S == delay) and (self.Slack() < slack)):
                    slack = self.Slack()
                    delay = S
                    self.Theta_x = copy.deepcopy(Theta_hat)
                    self.P_x = copy.deepcopy(P_hat)
            print(self.Theta_x)
            self.Remove()
        except ValueError:
            print(ValueError)

    def deltaSDelay(self, route: list):
        delay: float = 0.0
        tripTime: float = 0.0
        for i in range(1, len(route['route']), 1):
            previousNode = route['route'][i - 1]
            currentNode = route['route'][i]
            currentDistance = self.distance(previousNode.getLatitude(), previousNode.getLongitude(),
                                            currentNode.getLatitude(), currentNode.getLongitude())
            tripTime += currentDistance / self.velocity
            if isinstance(currentNode, Ds):
                delay += max(0, (tripTime + self.time_buffer) - (
                        currentNode.getDeadLine() + currentNode.get_timeRequest()))
        return delay

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
                    tempList = copy.deepcopy(currentDriver.route)
                    tempList.insert(i, currentParedRestaurent)
                    tempList.insert(j, order)
                    delayTime = self.deltaSDelay(tempList)

                    if minDelayTime > delayTime:
                        minDelayTime = delayTime
                        first = i
                        second = j

            currentDriver.route.insert(first, currentParedRestaurent)
            currentDriver.route.insert(second, order)
        return Theta_hat
    # main function

    def Slack(self):
        totalSlack: int = 0
        for routePerVehicle in self.Theta_x:
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

    def slackDelay(self, route):
        delay: int = 0
        tripTime: int = 0
        currentDriver = self.vehiceList[route["driverId"] - 1]
        currentRoute: list = copy.deepcopy(route['route'])
        currentRoute.append(currentDriver)
        for i in range(1, len(currentRoute), 1):
            currentDistance = self.distance(currentRoute[i - 1].getLatitude(), currentRoute[i - 1].getLongitude(),
                                            currentRoute[i].getLatitude(),
                                            currentRoute[i].getLongitude())
            tripTime += currentDistance / self.velocity
            if isinstance(currentRoute[i], Ds):
                delay += max(0, currentRoute[i].getDeadLine() -
                             tripTime - self.time_buffer)
        return delay

    def TotalDelay(self):
        totalSlack: int = 0
        for routePerVehicle in self.Theta_x:
            totalSlack += self.deltaSDelay(routePerVehicle)
        return totalSlack

    def Remove(self):
        for pospondedOrder in self.P_x:
            currentPairedDriver = self.vehiceList[pospondedOrder.getDriverId() - 1]
            targetRoute: list = next(
                (route for route in self.Theta_x if route.get("driverId") == currentPairedDriver.get_id()), [])
            ans = [node for node in targetRoute['route'] if
                   ((isinstance(node, Ds) and node.getId() != pospondedOrder.getId()) or
                    (isinstance(node, restaurant) and node.getOrderId() != pospondedOrder.getId()))]
            targetRoute['route'] = copy.deepcopy(ans[:])

    def Postponement(self, P_hat, D, p_max, t_Pmax):
        # P_hat,D, p_max, t_Pmax have the description
        # if Theta_hat != D:  # I don't know how to get current route plan
        if len(P_hat) == 0:  # if postponement set is empty
            return True
        elif len(P_hat) < self.maxLengthPost:  # if number of postponement <= max of postponement
            # The time difference with the first order of P_hat and check whether <= max
            if D.t - P_hat[0].t < t_Pmax:
                # of poatponement time
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
