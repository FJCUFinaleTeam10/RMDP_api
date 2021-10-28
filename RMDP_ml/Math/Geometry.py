import logging
import math
import random

from shapely.geometry import LineString
from shapely.geometry import Point
from math import cos, sin
from numba import jit


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


@jit(nopython=True)
def randomLocation(Longitude, Latitude, Radius):
    try:
        return [random.uniform(float(Latitude), float(Latitude) + float(Radius)),
                random.uniform(float(Longitude), float(Longitude) + float(Radius))]
    except Exception as e:
        logging.critical(e, exc_info=True)


@jit(nopython=True)
def coorDistance(lat1, lon1, lat2, lon2):
    try:
        p = math.pi / 180
        a = 0.5 - math.cos((lat2 - lat1) * p) / 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (
                1 - math.cos((lon2 - lon1) * p)) / 2
        return 12742 * math.asin(math.sqrt(a))  # 2*R*asin... '''

    except Exception as e:
        logging.critical(e, exc_info=True)
