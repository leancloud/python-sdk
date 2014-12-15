# coding: utf-8

import json

import requests

from leancloud import settings

__author__ = 'asaka <lan@leancloud.rocks>'


BASE_URL = settings.CN_BASE_URL + '/1.1'


def need_sdk_init(func):
    def new_func(*args, **kwargs):
        if settings.APP_ID is None or settings.KEY is None:
            raise RuntimeError('LeanCloud SDK must be initialized')
        return func(*args, **kwargs)
    return new_func


@need_sdk_init
def get(url, params):
    for k, v in params.iteritems():
        if isinstance(v, dict):
            params[k] = json.dumps(v)
    response = requests.get(BASE_URL + url, headers={
        'X-AVOSCloud-Application-Id': settings.APP_ID,
        'X-AVOSCloud-Application-Key': settings.KEY,
    }, params=params)
    return response


@need_sdk_init
def post(url, params):
    response = requests.post(BASE_URL + url, headers={
        'X-AVOSCloud-Application-Id': settings.APP_ID,
        'X-AVOSCloud-Application-Key': settings.KEY,
    }, json=params)
    return response


@need_sdk_init
def put(url, params):
    response = requests.post(BASE_URL + url, headers={
        'X-AVOSCloud-Application-Id': settings.APP_ID,
        'X-AVOSCloud-Application-Key': settings.KEY,
    }, json=params)
    return response


@need_sdk_init
def delete(url, params=None):
    if params is None:
        params = {}
    response = requests.delete(BASE_URL + url, headers={
        'X-AVOSCloud-Application-Id': settings.APP_ID,
        'X-AVOSCloud-Application-Key': settings.KEY,
    }, json=params)
    return response
