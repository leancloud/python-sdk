# coding: utf-8

from leancloud import Object


__author__ = 'asaka <lan@leancloud.rocks>'


class File(Object):
    def __init__(self, name, data, type_):
        self.name = name
