import logging
import math
from random import random

from numpy import ones, vstack
from numpy.linalg import lstsq
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString
from shapely.geometry import Point
from numpy import ones, vstack
from numpy.linalg import lstsq


def lineSolution(x1: float, x2: float, y1: float, y2: float):
    points = [(x1, x2), (y1, y2)]
    x_coords, y_coords = zip(*points)
    A = vstack([x_coords, ones(len(x_coords))]).T
    a, b = lstsq(A, y_coords)[0]
    print("Line Solution is y = {a}x + {b}".format(a=a, b=b))
    return a, b


def showCircle():
    x = np.linspace(-1.0, 1.0, 100)
    y = np.linspace(-1.0, 1.0, 100)
    X, Y = np.meshgrid(x, y)
    F = X ** 2 + Y ** 2 - 0.6
    plt.contour(X, Y, F, [0])
    plt.show()


def interSectionCircleAndLine(centerX: float, centerY: float, Radius: float, aX: float, aY: float, bX: float,
                              bY: float):
    # CenterPoint = Point(centerX, centerY)
    # circle = CenterPoint.buffer(Radius).boundary
    # lineEquation = LineString([(aX, aY), (bX, bY)])
    # intersection = circle.intersection(lineEquation)

    circleCoordinate = Point(centerX, centerY)
    circle = circleCoordinate.buffer(Radius).boundary
    line = LineString([(aX, aY), (bX, bY)])
    intersection = circle.intersection(line)

    # print(i.geoms[0].coords[0])
    # print(i.geoms[1].coords[0])
    # print(intersection.x, intersection.y)
    return intersection.x, intersection.y


def randomLocation(self, Longitude, Latitude, Radius):
    return [random.uniform(float(Latitude), float(Latitude) + float(Radius)),
            random.uniform(float(Longitude), float(Longitude) + float(Radius))]


def coorDistance(self, lat1, lon1, lat2, lon2):
    try:
        a = 0.5 - math.cos((lat2 - lat1) * self.p) / 2 + math.cos(lat1 * self.p) * math.cos(lat2 * self.p) * (
                1 - math.cos((lon2 - lon1) * self.p)) / 2
        return 12742 * math.asin(math.sqrt(a))  # 2*R*asin...
    except Exception as e:
        logging.critical(e, exc_info=True)
