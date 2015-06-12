# coding: utf-8

import json

import requests

import leancloud
from leancloud import utils

__author__ = 'asaka <lan@leancloud.rocks>'


APP_ID = None
APP_KEY = None
MASTER_KEY = None
USE_PRODUCTION = 1

CN_BASE_URL = 'https://api.leancloud.cn'
US_BASE_URL = 'https://avoscloud.us'

SERVER_VERSION = '1.1'
SDK_VERSION = '1.0.0'
BASE_URL = CN_BASE_URL + '/' + SERVER_VERSION
TIMEOUT_SECONDS = 15


def init(app_id, app_key=None, master_key=None):
    """初始化 LeanCloud 的 AppId / AppKey / MasterKey

    :type app_id: basestring
    :param app_id: 应用的 Application ID
    :type app_key: None or basestring
    :param app_key: 应用的 Application Key
    :type master_key: None or basestring
    :param master_key: 应用的 Master Key
    """
    if (not app_key) and (not master_key):
        raise RuntimeError('app_key or master_key must be specified')
    # if app_key and master_key:
    #     raise RuntimeError('app_key and master_key can\'t be specified both')
    global APP_ID, APP_KEY, MASTER_KEY
    APP_ID = app_id
    APP_KEY = app_key
    MASTER_KEY = master_key


def need_init(func):
    def new_func(*args, **kwargs):
        if APP_ID is None:
            raise RuntimeError('LeanCloud SDK must be initialized')

        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'X-AVOSCloud-Application-Id': APP_ID,
            'X-AVOSCloud-Application-Production': USE_PRODUCTION,
            'User-Agent': 'AVOS Cloud python-{0} SDK'.format(leancloud.__version__),
        }

        if MASTER_KEY:
            headers['X-AVOSCloud-Master-Key'] = MASTER_KEY
        else:
            headers['X-AVOSCloud-Application-Key'] = APP_KEY

        user = leancloud.User.get_current()
        if user:
            headers['X-AVOSCloud-Session-Token'] = user._session_token

        kwargs['headers'] = headers

        return func(*args, **kwargs)
    return new_func


def use_production(flag):
    global USE_PRODUCTION
    USE_PRODUCTION = 1 if flag else 0


def check_error(func):
    def new_func(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.headers['Content-Type'] == 'text/html':
            raise leancloud.LeanCloudError(-1, 'Bad Request')

        content = utils.response_to_json(response)

        if 'error' in content:
            raise leancloud.LeanCloudError(content.get('code', 1), content.get('error', 'Unknown Error'))

        return response
    return new_func


@need_init
@check_error
def get(url, params, headers=None):
    for k, v in params.iteritems():
        if isinstance(v, dict):
            params[k] = json.dumps(v)
    response = requests.get(BASE_URL + url, headers=headers, params=params, timeout=TIMEOUT_SECONDS)
    return response


@need_init
@check_error
def post(url, params, headers=None):
    response = requests.post(BASE_URL + url, headers=headers, data=json.dumps(params), timeout=TIMEOUT_SECONDS)
    return response


@need_init
@check_error
def put(url, params, headers=None):
    response = requests.put(BASE_URL + url, headers=headers, data=json.dumps(params), timeout=TIMEOUT_SECONDS)
    return response


@need_init
@check_error
def delete(url, params=None, headers=None):
    response = requests.delete(BASE_URL + url, headers=headers, data=json.dumps(params), timeout=TIMEOUT_SECONDS)
    return response
