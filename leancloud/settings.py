# coding: utf-8

__author__ = 'asaka <lan@leancloud.rocks>'

session = None

APP_ID = None
KEY = None

CN_BASE_URL = 'https://cn.avoscloud.com'
US_BASE_URL = 'https://us.avoscloud.com'


def init(app_id, key):
    global APP_ID, KEY, session
    APP_ID = app_id
    KEY = key
