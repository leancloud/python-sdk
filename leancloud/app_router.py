# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import time
import threading

import requests


class AppRouter(object):
    def __init__(self, app_id, region):
        self.app_id = app_id
        self.region = region
        self.hosts = {}
        self.session = requests.Session()
        self.lock = threading.Lock()
        self.expired_at = 0
        if region == 'US':
            self.hosts['api'] = 'us-api.leancloud.cn'
            self.hosts['engine'] = 'us-api.leancloud.cn'
            self.hosts['stats'] = 'us-api.leancloud.cn'
            self.hosts['push'] = 'us-api.leancloud.cn'
        elif region == 'CN':
            if app_id.endswith('-9Nh9j0Va'):
                self.hosts['api'] = 'e1-api.leancloud.cn'
                self.hosts['engine'] = 'e1-api.leancloud.cn'
                self.hosts['stats'] = 'e1-api.leancloud.cn'
                self.hosts['push'] = 'e1-api.leancloud.cn'
            else:
                prefix = app_id[:8].lower()
                self.hosts['api'] = '{}.api.lncld.net'.format(prefix)
                self.hosts['engine'] = '{}.engine.lncld.net'.format(prefix)
                self.hosts['stats'] = '{}.stats.lncld.net'.format(prefix)
                self.hosts['push'] = '{}.push.lncld.net'.format(prefix)
        else:
            raise RuntimeError('invalid region: {}'.format(region))

    def get(self, type_):
        if self.region == 'US':
            # US region dose not support app router stuff
            return self.hosts[type_]

        with self.lock:
            if time.time() > self.expired_at:
                self.expired_at += 600
                threading.Thread(target=self.refresh).start()
            return self.hosts[type_]

    def refresh(self):
        url = 'https://app-router.leancloud.cn/2/route?appId={}'.format(self.app_id)
        try:
            result = self.session.get(url, timeout=5).json()
            with self.lock:
                self.update(result)
        except Exception as e:
            print('refresh app router failed:', e, file=sys.stderr)

    def update(self, content):
        self.hosts['api'] = content['api_server']
        self.hosts['engine'] = content['engine_server']
        self.hosts['stats'] = content['stats_server']
        self.hosts['push'] = content['push_server']
        self.expired_at = time.time() + content['ttl']
