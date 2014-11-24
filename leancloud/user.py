# coding: utf-8

__author__ = 'asaka'

from leancloud import Object


class User(Object):
    def __init__(self):
        self._is_current_user = False
