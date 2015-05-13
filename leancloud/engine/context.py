# coding: utf-8

from werkzeug.local import Local
from werkzeug.local import LocalManager

__author__ = 'asaka <lan@leancloud.rocks>'

local = Local()
local_manager = LocalManager([local])
