# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import time
import hashlib
import functools

import six
import requests

import leancloud
from leancloud import utils
from leancloud.app_router import AppRouter

__author__ = "asaka <lan@leancloud.rocks>"


APP_ID = None
APP_KEY = None
MASTER_KEY = None
HOOK_KEY = None
if os.getenv("LEANCLOUD_APP_ENV") == "production":
    USE_PRODUCTION = "1"
elif os.getenv("LEANCLOUD_APP_ENV") == "stage":
    USE_PRODUCTION = "0"
else:  # probably on local machine
    if os.getenv("LEAN_CLI_HAVE_STAGING") == "true":
        USE_PRODUCTION = "0"
    else:  # free trial instance only
        USE_PRODUCTION = "1"

USE_HTTPS = True
# 兼容老版本，如果 USE_MASTER_KEY 为 None ，并且 MASTER_KEY 不为 None，则使用 MASTER_KEY
# 否则依据 USE_MASTER_KEY 来决定是否使用 MASTER_KEY
USE_MASTER_KEY = None
REGION = "CN"

app_router = None
session = requests.Session()
request_hooks = {}

SERVER_VERSION = "1.1"

TIMEOUT_SECONDS = 15


def init(app_id, app_key=None, master_key=None, hook_key=None):
    """初始化 LeanCloud 的 AppId / AppKey / MasterKey

    :type app_id: string_types
    :param app_id: 应用的 Application ID
    :type app_key: None or string_types
    :param app_key: 应用的 Application Key
    :type master_key: None or string_types
    :param master_key: 应用的 Master Key
    :param hook_key: application's hook key
    :type hook_key: None or string_type
    """
    if (not app_key) and (not master_key):
        raise RuntimeError("app_key or master_key must be specified")
    global APP_ID, APP_KEY, MASTER_KEY, HOOK_KEY
    APP_ID = app_id
    APP_KEY = app_key
    MASTER_KEY = master_key
    if hook_key:
        HOOK_KEY = hook_key
    else:
        HOOK_KEY = os.environ.get("LEANCLOUD_APP_HOOK_KEY")


def need_init(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        if APP_ID is None:
            raise RuntimeError("LeanCloud SDK must be initialized")

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "X-LC-Id": APP_ID,
            "X-LC-Prod": USE_PRODUCTION,
            "User-Agent": "AVOS Cloud python-{0} SDK ({1}.{2})".format(
                leancloud.__version__,
                leancloud.version_info.major,
                leancloud.version_info.minor,
            ),
        }
        md5sum = hashlib.md5()
        current_time = six.text_type(int(time.time() * 1000))
        if (USE_MASTER_KEY is None and MASTER_KEY) or USE_MASTER_KEY is True:
            md5sum.update((current_time + MASTER_KEY).encode("utf-8"))
            headers["X-LC-Sign"] = md5sum.hexdigest() + "," + current_time + ",master"
        else:
            # In python 2.x, you can feed this object with arbitrary
            # strings using the update() method, but in python 3.x,
            # you should feed with bytes-like objects.
            md5sum.update((current_time + APP_KEY).encode("utf-8"))
            headers["X-LC-Sign"] = md5sum.hexdigest() + "," + current_time

        user = leancloud.User.get_current()
        if user:
            headers["X-LC-Session"] = user._session_token

        return func(headers=headers, *args, **kwargs)

    return new_func


def get_url(part):
    # try to use the base URL from environ
    url = os.environ.get("LC_API_SERVER") or os.environ.get("LEANCLOUD_API_SERVER")
    if url:
        return "{}/{}{}".format(url, SERVER_VERSION, part)

    global app_router
    if app_router is None:
        app_router = AppRouter(APP_ID, REGION)

    if part.startswith("/push") or part.startswith("/installations"):
        host = app_router.get("push")
    elif part.startswith("/collect"):
        host = app_router.get("stats")
    elif part.startswith("/functions") or part.startswith("/call"):
        host = app_router.get("engine")
    else:
        host = app_router.get("api")
    r = {
        "schema": "https" if USE_HTTPS else "http",
        "version": SERVER_VERSION,
        "host": host,
        "part": part,
    }
    return "{schema}://{host}/{version}{part}".format(**r)


def use_production(flag):
    """调用生产环境 / 开发环境的 cloud func / cloud hook
    默认调用生产环境。
    """
    global USE_PRODUCTION
    USE_PRODUCTION = "1" if flag else "0"


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
        raise RuntimeError("LeanCloud SDK master key not specified")
    USE_MASTER_KEY = True


def check_error(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        response = func(*args, **kwargs)
        assert isinstance(response, requests.Response)
        if response.headers.get("Content-Type") == "text/html":
            raise leancloud.LeanCloudError(-1, "Bad Request")

        content = response.json()

        if "error" in content:
            raise leancloud.LeanCloudError(
                content.get("code", 1), content.get("error", "Unknown Error")
            )

        return response

    return new_func


def use_region(region):
    if region not in ("CN", "US"):
        raise ValueError("currently no nodes in the region")

    global REGION
    REGION = region


def get_server_time():
    response = check_error(session.get)(get_url("/date"), timeout=TIMEOUT_SECONDS)
    return utils.decode("iso", response.json())


def get_app_info():
    return {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "master_key": MASTER_KEY,
        "hook_key": HOOK_KEY,
    }


@need_init
@check_error
def get(url, params=None, headers=None):
    if not params:
        params = {}
    else:
        for k, v in six.iteritems(params):
            if isinstance(v, dict):
                params[k] = json.dumps(v, separators=(",", ":"))
    response = session.get(
        get_url(url),
        headers=headers,
        params=params,
        timeout=TIMEOUT_SECONDS,
        hooks=request_hooks,
    )
    return response


@need_init
@check_error
def post(url, params, headers=None):
    response = session.post(
        get_url(url),
        headers=headers,
        data=json.dumps(params, separators=(",", ":")),
        timeout=TIMEOUT_SECONDS,
        hooks=request_hooks,
    )
    return response


@need_init
@check_error
def put(url, params, headers=None):
    response = session.put(
        get_url(url),
        headers=headers,
        data=json.dumps(params, separators=(",", ":")),
        timeout=TIMEOUT_SECONDS,
        hooks=request_hooks,
    )
    return response


@need_init
@check_error
def delete(url, params=None, headers=None):
    response = session.delete(
        get_url(url),
        headers=headers,
        data=json.dumps(params, separators=(",", ":")),
        timeout=TIMEOUT_SECONDS,
        hooks=request_hooks,
    )
    return response
