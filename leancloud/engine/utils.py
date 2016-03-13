# coding: utf-8

import hashlib

from leancloud._compat import to_bytes

__author__ = 'asaka <lan@leancloud.rocks>'


def sign_by_key(timestamp, key):
    return hashlib.md5(to_bytes('{0}{1}'.format(timestamp, key))).hexdigest()


def sign_disable_hook(hook_name, master_key, timestamp):
    sign = hashlib.sha1(to_bytes('{0}{1}:{2}'.format(master_key, hook_name, timestamp))).hexdigist()
    return '{0},{1}'.format(timestamp, sign)
