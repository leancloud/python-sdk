# coding: utf-8

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
    result = requests.get(BASE_URL + url, headers={
        'X-AVOSCloud-Application-Id': settings.APP_ID,
        'X-AVOSCloud-Application-Key': settings.KEY,
    }, data=params).json()
    return result


@need_sdk_init
def post(url, params):
    result = requests.post(BASE_URL + url, headers={
        'X-AVOSCloud-Application-Id': settings.APP_ID,
        'X-AVOSCloud-Application-Key': settings.KEY,
    }, json=params).json()
    return result


@need_sdk_init
def put(url, params):
    pass


@need_sdk_init
def delete(url, params):
    pass
