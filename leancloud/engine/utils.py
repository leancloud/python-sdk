# coding: utf-8

import time
import hashlib

import leancloud
from leancloud._compat import to_bytes

__author__ = 'asaka <lan@leancloud.rocks>'


def sign_by_key(timestamp, key):
    return hashlib.md5(to_bytes('{0}{1}'.format(timestamp, key))).hexdigest()
