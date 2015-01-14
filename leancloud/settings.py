# coding: utf-8

__author__ = 'asaka <lan@leancloud.rocks>'


APP_ID = None
APP_KEY = None
MASTER_KEY = None

CN_BASE_URL = 'https://cn.avoscloud.com'
US_BASE_URL = 'https://us.avoscloud.com'


def init(app_id, app_key=None, master_key=None):
    if (not app_key) and (not master_key):
        raise RuntimeError('app_key or master_key must be specified')
    if app_key and master_key:
        raise RuntimeError('app_key and master_key can\'t be specified both')
    global APP_ID, APP_KEY, MASTER_KEY
    APP_ID = app_id
    APP_KEY = app_key
    MASTER_KEY = master_key
