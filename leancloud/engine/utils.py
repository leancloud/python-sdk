# coding: utf-8

import hashlib

__author__ = 'asaka <lan@leancloud.rocks>'


def sign_by_key(timestamp, key):
    return hashlib.md5('{}{}'.format(timestamp, key)).hexdigest()
