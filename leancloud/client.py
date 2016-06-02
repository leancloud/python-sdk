# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import time
import hashlib
import requests

import leancloud
from leancloud import utils
from leancloud._compat import iteritems
from leancloud._compat import to_bytes
from leancloud.app_router import AppRouter

__author__ = 'asaka <lan@leancloud.rocks>'


APP_ID = None
APP_KEY = None
MASTER_KEY = None
USE_PRODUCTION = '1'
USE_HTTPS = True
# 兼容老版本，如果 USE_MASTER_KEY 为 None ，并且 MASTER_KEY 不为 None，则使用 MASTER_KEY
# 否则依据 USE_MASTER_KEY 来决定是否使用 MASTER_KEY
USE_MASTER_KEY = None
REGION = 'CN'

app_router = None

SERVER_URLS = {
    'CN': 'api.leancloud.cn',
    'US': 'us-api.leancloud.cn',
}

SERVER_VERSION = '1.1'
SDK_VERSION = '1.0.0'

TIMEOUT_SECONDS = 15


def init(app_id, app_key=None, master_key=None):
    """初始化 LeanCloud 的 AppId / AppKey / MasterKey

    :type app_id: string_types
    :param app_id: 应用的 Application ID
    :type app_key: None or string_types
    :param app_key: 应用的 Application Key
    :type master_key: None or string_types
    :param master_key: 应用的 Master Key
    """
    if (not app_key) and (not master_key):
        raise RuntimeError('app_key or master_key must be specified')
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
        md5sum = hashlib.md5()
        current_time = str(int(time.time() * 1000))
        if (USE_MASTER_KEY is None and MASTER_KEY) or USE_MASTER_KEY is True:
            # md5sum.update(current_time + MASTER_KEY)
            # headers['X-AVOSCloud-Request-Sign'] = md5sum.hexdigest() + ',' + current_time + ',master'
            headers['X-AVOSCloud-Master-Key'] = MASTER_KEY
        else:
            # In python 2.x, you can feed this object with arbitrary
            # strings using the update() method, but in python 3.x,
            # you should feed with bytes-like objects.
            md5sum.update(to_bytes(current_time + APP_KEY))
            headers['X-AVOSCloud-Request-Sign'] = md5sum.hexdigest() + ',' + current_time

        user = leancloud.User.get_current()
        if user:
            headers['X-AVOSCloud-Session-Token'] = user._session_token

        return func(headers=headers, *args, **kwargs)
    return new_func


def get_base_url():
    # try to use the base URL from environ
    url = os.environ.get('LC_API_SERVER') or os.environ.get('LEANCLOUD_API_SERVER')
    if url:
        return '{}/{}'.format(url, SERVER_VERSION)

    if REGION == 'US':
        # use the hard coded base URL if region is US
        host = SERVER_URLS[REGION]
    else:
        # use base URL from app router
        global app_router
        if app_router is None:
            app_router = AppRouter(APP_ID)
        host = app_router.get()
    r = {
        'schema': 'https' if USE_HTTPS else 'http',
        'version': SERVER_VERSION,
        'host': host,
    }
    return '{schema}://{host}/{version}'.format(**r)


def use_production(flag):
    """调用生产环境 / 开发环境的 cloud func / cloud hook
    默认调用生产环境。
    """
    global USE_PRODUCTION
    USE_PRODUCTION = '1' if flag else '0'


def use_master_key(flag=True):
    """是否使用 master key 发送请求。
    如果不调用此函数，会根据 leancloud.init 的参数来决定是否使用 master key。

    :type flag: bool
    """
    global USE_MASTER_KEY
    if not flag:
        USE_MASTER_KEY = False
        return
    if not MASTER_KEY:
        raise RuntimeError('LeanCloud SDK master key not specified')
    USE_MASTER_KEY = True


# def use_https(flag=True):
#     """是否启用 HTTPS 和 LeanCloud 存储服务器通讯。
#     默认启用，在 LeanEngine 环境下关闭可以大幅提高 LeanCloud 存储服务查询性能。
#
#     :type flag: bool
#     """
#     global USE_HTTPS
#     if not flag:
#         USE_HTTPS = False
#     else:
#         USE_HTTPS = True


def check_error(func):
    def new_func(*args, **kwargs):
        response = func(*args, **kwargs)
        assert isinstance(response, requests.Response)
        if response.headers.get('Content-Type') == 'text/html':
            print(response.status_code)
            print(response.content)
            raise leancloud.LeanCloudError(-1, 'Bad Request')

        content = response.json()

        if 'error' in content:
            raise leancloud.LeanCloudError(content.get('code', 1), content.get('error', 'Unknown Error'))

        return response
    return new_func


def region_redirect(func):
    def new_func(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.status_code == 307:
            # we are requests another region's API server, and it told us to request another API server
            content = response.json()
            if app_router:
                app_router.update(content)
                response = func(*args, **kwargs)
        return response

    return new_func


def use_region(region):
    if region not in SERVER_URLS:
        raise ValueError('currently no nodes in the region')

    global REGION
    REGION = region


def get_server_time():
    response = requests.get(get_base_url() + '/date')
    content = json.loads(response.text)
    return utils.decode('iso', content)


def get_app_info():
    return {
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'master_key': MASTER_KEY,
    }


@need_init
@region_redirect
@check_error
def get(url, params=None, headers=None):
    if not params:
        params = {}
    else:
        for k, v in iteritems(params):
            if isinstance(v, dict):
                params[k] = json.dumps(v, separators=(',', ':'))
    response = requests.get(get_base_url() + url, headers=headers, params=params, timeout=TIMEOUT_SECONDS)
    return response


@need_init
@region_redirect
@check_error
def post(url, params, headers=None):
    response = requests.post(get_base_url() + url, headers=headers, data=json.dumps(params, separators=(',', ':')), timeout=TIMEOUT_SECONDS)
    return response


@need_init
@region_redirect
@check_error
def put(url, params, headers=None):
    response = requests.put(get_base_url() + url, headers=headers, data=json.dumps(params, separators=(',', ':')), timeout=TIMEOUT_SECONDS)
    return response


@need_init
@region_redirect
@check_error
def delete(url, params=None, headers=None):
    response = requests.delete(get_base_url() + url, headers=headers, data=json.dumps(params, separators=(',', ':')), timeout=TIMEOUT_SECONDS)
    return response
