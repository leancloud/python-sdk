# coding: utf-8

__author__ = 'asaka <lan@leancloud.rocks>'


class LeanCloudError(Exception):
    def __init__(self, code, error):
        self.code = code
        self.error = error

        self.args = (u'[{}] {}'.format(self.code, self.error), )
