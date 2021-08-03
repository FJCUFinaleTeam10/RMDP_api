import copy
# from generatingData import generateTestData
# from Math.Geometry import interSectionCircleAndLine
import itertools
import math

from driver.models import driver
from order.models import order
from restaurant.models import restaurant


class RMDP:
    def __init__(self, delay: int, maxLengthPost: int, maxTimePost: int,
                 capacity: int, velocity: int, restaurantPrepareTime: int):

        # self.Ds_0 = generateTestData.importOrderValue()

        self.x = 0
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

    def runRMDP(self, state: int, unAssignOrder: list):

        restaurantList = restaurant.objects.all()
        vehicleList = driver.objects.all()
        unAssignOrder = order.objects.filter()
        P_x = []
        delay: float = float("inf")
        slack = 0

        # counter for n! type sequences
        unassignedOrderPermutation = list(itertools.permutations(unAssignOrder))
        for permutation in unassignedOrderPermutation:
            Theta_hat = copy.deepcopy(vehicleList)  # Candidate route plan
            P_hat = copy.deepcopy(P_x)

            for D in permutation:

                currentPairdDriver = self.FindVehicle(D)
                D.setDriverId(currentPairdDriver.get_id())
                currentPairdRestaurent = copy.deepcopy(restaurantList[D.getRestaurantId() - 1])
                currentPairdRestaurent.setOrderId(D.getId())
                currentPairdDriver.setCurrentCapacity(currentPairdDriver.getCurrentCapacity() + 1)
                self.AssignOrder(Theta_hat, D, currentPairdDriver, currentPairdRestaurent)
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
                            PairedRestaurent = copy.deepcopy(restaurantList[pospondedOrder.getRestaurantId() - 1])
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

    def AssignOrder(self, Theta_hat, D, V, currentParedRestaurent):
        currentRoute: list = next((route for route in Theta_hat if route.get("driverId") == V.get_id()), [])

        if not currentRoute['route']:
            currentRoute['route'].append(currentParedRestaurent)
            currentRoute['route'].append(D)

        else:
            first: int = 0
            second: int = 1
            minDelayTime = float('inf')
            for i in range(0, len(currentRoute), 1):  # control Restaurant
                for j in range(i + 1, len(currentRoute) + 2, 1):  # find all the possible positioins of new order
                    tempList = copy.deepcopy(currentRoute)
                    tempList["route"].insert(i, currentParedRestaurent)
                    tempList["route"].insert(j, D)
                    delayTime = self.deltaSDelay(tempList)

                    if minDelayTime > delayTime:
                        minDelayTime = delayTime
                        first = i
                        second = j

            currentRoute['route'].insert(first, currentParedRestaurent)
            currentRoute['route'].insert(second, D)

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
        return (self.distance(driv.x, driv.y, res.xPosition, res.yPosition) +
                self.distance(res.xPosition, res.yPosition, order.x, order.y)) / self.velocity

    def FindVehicle(self, Order):
        OrderRestaurant = self.restaurantList[Order.getRestaurantId() - 1]
        minTimeDriver = self.vehiceList[0]
        minTimeTolTal = float('inf')
        handleDriver = [driver for driver in self.vehiceList if driver.getCurrentCapacity() < self.capacity]
        for currentDriver in handleDriver:
            currenTripTime: float = self.tripTime(currentDriver, OrderRestaurant, Order)
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



test = RMDP()
test.runRMDP()