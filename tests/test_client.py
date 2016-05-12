# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import datetime

from werkzeug.wrappers import Request
from wsgi_intercept import requests_intercept, add_wsgi_intercept

import leancloud
from leancloud import client
from leancloud.app_router import AppRouter


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


# def test_get_base_url():
#     leancloud.use_https(False)
#     assert client.get_base_url().startswith('http://')
#     leancloud.use_https(True)
#     assert client.get_base_url().startswith('https://')


def test_get_server_time():
    assert type(client.get_server_time()) == datetime.datetime


def test_redirect_region():
    if client.REGION == 'US':
        # US region server doesn't support app router now
        return
    # setup
    old_app_router = client.app_router
    client.app_router = AppRouter('test_app_id')
    requests_intercept.install()

    def fake_app_router(environ, start_response):
        assert environ['PATH_INFO'] == '/1/route'
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps({
            'api_server': 'fake-redirect-server',
            'ttl': 3600,
        })]

    host, port = 'app-router.leancloud.cn', 443
    add_wsgi_intercept(host, port, lambda: fake_app_router)

    def fake_redirect_server(environ, start_response):
        start_response('307', [('Content-Type', 'application/json')])
        return [json.dumps({
            'api_server': 'fake-api-server',
            'ttl': 3600,
        })]

    host, port = 'fake-redirect-server', 443
    add_wsgi_intercept(host, port, lambda: fake_redirect_server)


    def fake_api_server(environ, start_response):
        start_response('200', [('Content-Type', 'application/json')])
        return [json.dumps({
            'result': 42,
        })]

    host, port = 'fake-api-server', 443
    add_wsgi_intercept(host, port, lambda: fake_api_server)

    # test
    assert client.get('/redirectme').json()['result'] == 42

    # teardown
    client.app_router = old_app_router
    requests_intercept.uninstall()
