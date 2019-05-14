# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json

from werkzeug.wrappers import Request  # type: ignore
from wsgi_intercept import requests_intercept, add_wsgi_intercept  # type: ignore

import leancloud
from leancloud import client
from leancloud.app_router import AppRouter #type: ignore


__author__ = 'asaka'


def test_use_production(): # type: () -> None
    assert client.is_prod() == '1'
    os.environ['LEANCLOUD_APP_ENV'] = 'stage'
    assert client.is_prod() == '0'
    os.environ['LEANCLOUD_APP_ENV'] = 'production'
    assert client.is_prod() == '1'

    os.environ['LEANCLOUD_APP_ENV'] = 'development'
    os.environ['LEAN_CLI_HAVE_STAGING'] = 'true'
    assert client.is_prod() == '0'
    os.environ['LEAN_CLI_HAVE_STAGING'] = 'false'
    assert client.is_prod() == '1'


def test_use_master_key(): # type: () -> None
    leancloud.init(os.environ['APP_ID'], os.environ['APP_KEY'], os.environ['MASTER_KEY'])
    assert client.USE_MASTER_KEY is None
    leancloud.use_master_key(True)
    assert client.USE_MASTER_KEY is True
    leancloud.use_master_key(False)
    assert client.USE_MASTER_KEY is False
