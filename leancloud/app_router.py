# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import time
import threading

import requests


class AppRouter(object):
    def __init__(self, app_id):
        self.lock = threading.Lock()
        self.app_id = app_id
        self.api_server = None
        self.expired_at = 0

    def get(self):
        if self.api_server is not None and self.expired_at > time.time():
            return self.api_server
        else:
            with self.lock:
                return self.refresh()

    def refresh(self):
        url = 'https://app-router.leancloud.cn/1/route?appId={}'.format(self.app_id)
        try:
            result = requests.get(url).json()
            self.update(result)
            return result['api_server']
        except Exception as e:
            print('refresh app router failed: ', e, file=sys.stderr)

    def update(self, content):
        self.api_server = content['api_server']
        self.expired_at = time.time() + content['ttl']
