# coding: utf-8

import os
import datetime

import leancloud
from leancloud import client


__author__ = 'asaka'


def test_use_production():
    assert client.USE_PRODUCTION == '1'
    leancloud.use_production(False)
    assert client.USE_PRODUCTION == '0'
    leancloud.use_production(True)
    assert client.USE_PRODUCTION == '1'


def test_use_master_key():
    leancloud.init(os.environ['APP_ID'], os.environ['APP_KEY'], os.environ['MASTER_KEY'])
    assert client.USE_MASTER_KEY is None
    leancloud.use_master_key(True)
    assert client.USE_MASTER_KEY is True
    leancloud.use_master_key(False)
    assert client.USE_MASTER_KEY is False


def test_get_server_time():
    assert type(client.get_server_time()) == datetime.datetime
