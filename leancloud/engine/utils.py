# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import hashlib

__author__ = 'asaka <lan@leancloud.rocks>'


def sign_by_key(timestamp, key):
    s = '{0}{1}'.format(timestamp, key)
    return hashlib.md5(s.encode('utf-8')).hexdigest()
