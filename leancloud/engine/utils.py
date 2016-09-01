# coding: utf-8

import time
import hashlib

import leancloud
from leancloud._compat import to_bytes

__author__ = 'asaka <lan@leancloud.rocks>'


def sign_by_key(timestamp, key):
    return hashlib.md5(to_bytes('{0}{1}'.format(timestamp, key))).hexdigest()


def verify_hook_sign(hook_name, master_key, sign):
    timestamp = int(sign.split(',')[0])
    if (timestamp - time.time() * 1000) > 60 * 60 * 10 * 1000:
        # sign is expired
        return False
    if not sign:
        return False
    return leancloud.utils.sign_hook(hook_name, master_key, timestamp) == sign
