# coding: utf-8

__author__ = 'asaka <lan@leancloud.rocks>'


class LeanCloudError(Exception):
    def __init__(self, code, error):
        self.code = code
        self.error = error

    def __str__(self):
        error = self.error if isinstance(self.error, str) else self.error.encode('utf-8', 'ignore')
        return '[{}] {}'.format(self.code, error)
