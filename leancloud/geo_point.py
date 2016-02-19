# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math


__author__ = 'asaka <lan@leancloud.rocks>'


class GeoPoint(object):
    def __init__(self, latitude=0, longitude=0):
        """

        :param latitude: 纬度
        :type latitude: int or float
        :param longitude: 经度
        :type longitude: int or float
        :return: GeoPoint
        """
        self._validate(latitude, longitude)
        self._latitude = latitude
        self._longitude = longitude

    @classmethod
    def _validate(cls, latitude, longitude):
        if latitude < -90.0:
            raise ValueError('GeoPoint latitude {0} < -90.0'.format(latitude))

        if latitude > 90.0:
            raise ValueError('GeoPoint latitude {0} > 90.0'.format(latitude))

        if longitude < -180.0:
            raise ValueError('GeoPoint longitude {0} < -180.0'.format(longitude))

        if longitude > 180.0:
            raise ValueError('GeoPoint longitude {0} > 180.0'.format(longitude))

    @property
    def latitude(self):
        """
        当前对象的纬度
        """
        return self._latitude

    @latitude.setter
    def latitude(self, latitude):
        self._validate(latitude, self.longitude)
        self._latitude = latitude

    @property
    def longitude(self):
        """
        当前对象的经度
        """
        return self._longitude

    @longitude.setter
    def longitude(self, longitude):
        self._validate(self.latitude, longitude)
        self._longitude = longitude

    def dump(self):
        self._validate(self.latitude, self.longitude)
        return {
            '__type': 'GeoPoint',
            'latitude': self.latitude,
            'longitude': self.longitude,
        }

    def radians_to(self, other):
        """
        Returns the distance from this GeoPoint to another in radians.

        :param other: point the other GeoPoint
        :type other: GeoPoint
        :rtype: float
        """
        d2r = math.pi / 180.0
        lat1rad = self.latitude * d2r
        long1rad = self.longitude * d2r

        lat2rad = other.latitude * d2r
        long2rad = other.longitude * d2r

        delta_lat = lat1rad - lat2rad
        delta_long = long1rad - long2rad

        sin_delta_lat_div2 = math.sin(delta_lat / 2.0)
        sin_delta_long_div2 = math.sin(delta_long / 2.0)

        a = ((sin_delta_lat_div2 * sin_delta_lat_div2) +
             (math.cos(lat1rad) * math.cos(lat2rad) *
              sin_delta_long_div2 * sin_delta_long_div2))
        a = min(1.0, a)
        return 2 * math.asin(math.sqrt(a))

    def kilometers_to(self, other):
        """
        Returns the distance from this GeoPoint to another in kilometers.

        :param other: point the other GeoPoint
        :type other: GeoPoint
        :rtype: float
        """
        return self.radians_to(other) * 6371.0

    def miles_to(self, other):
        """
        Returns the distance from this GeoPoint to another in miles.

        :param other: point the other GeoPoint
        :type other: GeoPoint
        :rtype: float
        """
        return self.radians_to(other) * 3958.8

    def __eq__(self, other):
        return \
            isinstance(other, GeoPoint) and \
            self.latitude == other.latitude and \
            self.longitude == other.longitude
