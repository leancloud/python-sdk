# coding: utf-8

"""LeanCloud Python SDK
"""

import logging

logger = logging.getLogger('iso8601.iso8601')
logger.setLevel(logging.CRITICAL)

import client
import push
from .push import Installation
from .acl import ACL
from .client import init
from .client import use_master_key
from .client import use_production
from .errors import LeanCloudError
from .file_ import File
from .geo_point import GeoPoint
from .object_ import Object
from .query import FriendshipQuery
from .query import Query
from .relation import Relation
from .user import User
from .role import Role
from .engine import Engine
from .engine import cloudfunc
from .engine import LeanEngineError
from .engine.https_redirect_middleware import HttpsRedirectMiddleware


__author__ = 'asaka <lan@leancloud.rocks>'
__version__ = '1.3.6'


__all__ = [
    'ACL',
    'Engine',
    'File',
    'FriendshipQuery',
    'GeoPoint',
    'HttpsRedirectMiddleware',
    'Installation',
    'LeanCloudError',
    'LeanEngineError',
    'Object',
    'Query',
    'Relation',
    'Role',
    'User',
    'client',
    'cloudfunc',
    'init',
    'push',
    'use_master_key',
    'use_production',
]
