# coding: utf-8

__author__ = 'asaka <lan@leancloud.rocks>'


class LeanCloudError(Exception):
    def __init__(self, code, error):
        self.code = code
        self.error = error

    def __str__(self):
        return '[{}] {}'.format(self.code, self.error.encode('utf-8'))
