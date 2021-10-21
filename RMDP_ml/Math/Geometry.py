import logging
import math
import random

from numpy import ones, vstack
from numpy.linalg import lstsq
from shapely.geometry import LineString
from shapely.geometry import Point
from math import cos, sin


def lineSolution(x1: float, x2: float, y1: float, y2: float):
    points = [(x1, x2), (y1, y2)]
    x_coords, y_coords = zip(*points)
    A = vstack([x_coords, ones(len(x_coords))]).T
    a, b = lstsq(A, y_coords)[0]
    print("Line Solution is y = {a}x + {b}".format(a=a, b=b))
    return a, b


def angleBetweenLineNHorizontalAxis(P1_x, P1_y, P2_x, P2_y):
    deltaY = P2_y - P1_y
    deltaX = P2_x - P1_x
    return math.atan2(deltaY, deltaX) * 180 / math.pi


def trigometric(angle, speed):
    dx = float(cos(angle) * speed)
    dy = float(sin(angle) * speed)
    return dx, dy


def dotproduct(v1, v2):
    return sum((a * b) for a, b in zip(v1, v2))


def length(v):
    return math.sqrt(dotproduct(v, v))


def caculateAngle(v1, v2):
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))


def interSectionCircleAndLine(center_Latitude: float, center_Longitude: float, Radius: float, a_Latitude: float,
                              a_Longitude: float, b_Latitude: float, b_Longitude: float):
    circle = Point(center_Latitude, center_Longitude).buffer(Radius).boundary
    line = LineString([(a_Latitude, a_Longitude), (b_Latitude, b_Longitude)])
    intersection = circle.intersection(line)
    return intersection.x, intersection.y


def randomLocation(Longitude, Latitude, Radius):
    try:
        return [random.uniform(float(Latitude), float(Latitude) + float(Radius)),
                random.uniform(float(Longitude), float(Longitude) + float(Radius))]
    except Exception as e:
        logging.critical(e, exc_info=True)


def coorDistance(lat1, lon1, lat2, lon2):
    try:
        p = math.pi / 180
        a = 0.5 - math.cos((lat2 - lat1) * p) / 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (
                1 - math.cos((lon2 - lon1) * p)) / 2
        return 12742 * math.asin(math.sqrt(a))  # 2*R*asin... '''

    except Exception as e:
        logging.critical(e, exc_info=True)
