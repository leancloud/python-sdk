# coding: utf-8

import leancloud
from leancloud import client


__author__ = 'asaka'


def test_use_production():
    assert client.USE_PRODUCTION == 1
    leancloud.use_production(False)
    assert client.USE_PRODUCTION == 0
    leancloud.use_production(True)
    assert client.USE_PRODUCTION == 1
