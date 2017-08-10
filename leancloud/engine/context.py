# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from werkzeug.local import Local
from werkzeug.local import LocalManager

__author__ = 'asaka <lan@leancloud.rocks>'


class Current(object):
    __slots__ = ['user', 'session_token', 'meta']
    def __init__(self):
        self.user = None
        self.session_token = None
        self.meta = None


local = Local()
local_manager = LocalManager([local])
