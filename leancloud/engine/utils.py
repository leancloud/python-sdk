# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import hashlib

import six


__author__ = "asaka <lan@leancloud.rocks>"


def sign_by_key(timestamp, key):
    s = "{0}{1}".format(timestamp, key)
    return hashlib.md5(s.encode("utf-8")).hexdigest()


if six.PY2:

    def to_native(s):
        if isinstance(s, unicode):  # noqa: F821
            return s.encode("utf-8")
        return s


else:

    def to_native(s):
        if isinstance(s, bytes):
            return s.decode("utf-8")
        return s
