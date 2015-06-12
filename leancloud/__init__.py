# coding: utf-8

"""LeanCloud Python SDK
"""

import client
import push
from .push import Installation
from .acl import ACL
from .client import init
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
__version__ = '1.1.0'


__all__ = [
    'ACL',
    'File',
    'HttpsRedirectMiddleware',
    'FriendshipQuery',
    'GeoPoint',
    'LeanCloudError',
    'LeanEngineError',
    'Object',
    'Query',
    'Relation',
    'User',
    'client',
    'use_production',
    'init',
    'push',
    'cloudfunc',
    'Role',
    'Installation',
    'Engine',
]
