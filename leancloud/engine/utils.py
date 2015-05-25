# coding: utf-8

import hashlib

__author__ = 'asaka <lan@leancloud.rocks>'


def sign_by_key(timestamp, key):
    return hashlib.md5('{0}{1}'.format(timestamp, key)).hexdigest()
