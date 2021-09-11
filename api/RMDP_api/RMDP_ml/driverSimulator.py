def updateDriverLocation(self, time):
    hasOrderVehicle: list = [routePerVehicle for routePerVehicle in self.Theta_x if
                             (routePerVehicle['route'] != [])]
    for route in hasOrderVehicle:
        currentDriver: driver = self.vehiceList[route.get("driverId") - 1]
        targetDestination = route['route'][0]
        travledDistance = currentDriver.getVelocity() * time
        estimatedDistance = distance(currentDriver.getLatitude(),
                                     currentDriver.getLongitude(),
                                     targetDestination.getLatitude(),
                                     targetDestination.getLongitude())
        if travledDistance > 0:

            if travledDistance >= estimatedDistance:
                currentDriver.setLatitude(targetDestination.getLatitude())
                currentDriver.setLongitude(targetDestination.getLongitude())
                route['route'].pop(0)
            else:
                updatedLon, updatedLat = interSectionCircleAndLine(currentDriver.getLongitude(),
                                                                   currentDriver.getLatitude(),
                                                                   travledDistance,
                                                                   currentDriver.getLongitude(),
                                                                   currentDriver.getLatitude(),
                                                                   targetDestination.getLongitude(),
                                                                   targetDestination.getLatitude())
                currentDriver.setLatitude(updatedLon)
                currentDriver.setLongitude(updatedLat)
