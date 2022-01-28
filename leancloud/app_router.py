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

        prefix = app_id[:8].lower()
        is_cn_n1 = False

        if region == "US":
            domain = "lncldglobal.com"
        elif region == "CN":
            if app_id.endswith("-9Nh9j0Va"):
                domain = "lncldapi.com"
            elif app_id.endswith("-MdYXbMMI"):
                domain = "lncldglobal.com"
            else:
                domain = "{}.lc-cn-n1-shared.com".format(prefix)
                is_cn_n1 = True
        else:
            raise RuntimeError("invalid region: {}".format(region))

        if is_cn_n1:
            self.hosts.update(dict.fromkeys(
                ["api", "engine", "stats", "push"], domain))
        else:
            self.hosts["api"] = "{}.api.{}".format(prefix, domain)
            self.hosts["engine"] = "{}.engine.{}".format(prefix, domain)
            self.hosts["stats"] = "{}.stats.{}".format(prefix, domain)
            self.hosts["push"] = "{}.push.{}".format(prefix, domain)

    def get(self, type_):
        with self.lock:
            if time.time() > self.expired_at:
                self.expired_at += 600
                threading.Thread(target=self.refresh).start()
            return self.hosts[type_]

    def refresh(self):
        url = "https://app-router.com/2/route?appId={}".format(self.app_id)
        try:
            result = self.session.get(url, timeout=5).json()
            with self.lock:
                self.update(result)
        except Exception as e:
            print("refresh app router failed:", e, file=sys.stderr)

    def update(self, content):
        self.hosts["api"] = content["api_server"]
        self.hosts["engine"] = content["engine_server"]
        self.hosts["stats"] = content["stats_server"]
        self.hosts["push"] = content["push_server"]
        self.expired_at = time.time() + content["ttl"]
