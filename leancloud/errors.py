# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__author__ = 'asaka <lan@leancloud.rocks>'


class LeanCloudError(Exception):
    def __init__(self, code, error):
        self.code = code
        self.error = error

    def __str__(self):
        error = self.error if isinstance(self.error, str) else self.error.encode('utf-8', 'ignore')
        return 'LeanCloudError: [{0}] {1}'.format(self.code, error)


class LeanCloudWarning(UserWarning):
    pass
