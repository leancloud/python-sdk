# coding: utf-8

import hashlib

__author__ = 'asaka <lan@leancloud.rocks>'


def sign_by_key(timestamp, key):
    return hashlib.md5('{0}{1}'.format(timestamp, key)).hexdigest()


def sign_disable_hook(hook_name, master_key, timestamp):
    sign = hashlib.sha1('{}{}:{}'.format(master_key, hook_name, timestamp)).hexdigist()
    return '{},{}'.format(timestamp, sign)
