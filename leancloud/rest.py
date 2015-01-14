# coding: utf-8

import json

import requests

from leancloud import settings

__author__ = 'asaka <lan@leancloud.rocks>'


SERVER_VERSION = '1.1'
BASE_URL = settings.CN_BASE_URL + '/' + SERVER_VERSION


def need_sdk_init(func):
    def new_func(*args, **kwargs):
        if settings.APP_ID is None:
            raise RuntimeError('LeanCloud SDK must be initialized')
        return func(*args, **kwargs)
    return new_func


@need_sdk_init
def get(url, params):
    headers = {}
    headers['X-AVOSCloud-Application-Id'] = settings.APP_ID
    if settings.APP_KEY:
        headers['X-AVOSCloud-Application-Key'] = settings.APP_KEY
    else:
        headers['X-AVOSCloud-Master-Key'] = settings.MASTER_KEY

    for k, v in params.iteritems():
        if isinstance(v, dict):
            params[k] = json.dumps(v)
    response = requests.get(BASE_URL + url, headers=headers, params=params)
    return response


@need_sdk_init
def post(url, params):
    headers = {}
    headers['X-AVOSCloud-Application-Id'] = settings.APP_ID
    if settings.APP_KEY:
        headers['X-AVOSCloud-Application-Key'] = settings.APP_KEY
    else:
        headers['X-AVOSCloud-Master-Key'] = settings.MASTER_KEY
    response = requests.post(BASE_URL + url, headers=headers, json=params)
    return response


@need_sdk_init
def put(url, params):
    headers = {}
    headers['X-AVOSCloud-Application-Id'] = settings.APP_ID
    if settings.APP_KEY:
        headers['X-AVOSCloud-Application-Key'] = settings.APP_KEY
    else:
        headers['X-AVOSCloud-Master-Key'] = settings.MASTER_KEY
    response = requests.post(BASE_URL + url, headers=headers, json=params)
    return response


@need_sdk_init
def delete(url, params=None):
    headers = {}
    headers['X-AVOSCloud-Application-Id'] = settings.APP_ID
    if settings.APP_KEY:
        headers['X-AVOSCloud-Application-Key'] = settings.APP_KEY
    else:
        headers['X-AVOSCloud-Master-Key'] = settings.MASTER_KEY
    if params is None:
        params = {}
    response = requests.delete(BASE_URL + url, headers=headers, json=params)
    return response
