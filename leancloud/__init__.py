# coding: utf-8

"""LeanCloud Python SDK
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import sys
import warnings

from . import client
from . import cloud
from . import push
from .acl import ACL
from .client import init
from .client import use_master_key
from .client import use_production
from .client import use_region
from .conversation import Conversation  # noqa: F401
from .engine import Engine
from .engine import LeanEngineError
from .engine.https_redirect_middleware import HttpsRedirectMiddleware
from .errors import LeanCloudError
from .errors import LeanCloudWarning
from .file_ import File
from .geo_point import GeoPoint
from .message import Message  # noqa: F401
from .object_ import Object
from .push import Installation
from .query import FriendshipQuery
from .query import Query
from .relation import Relation
from .role import Role
from .status import InboxQuery
from .status import Status
from .sys_message import SysMessage
from .user import User

logger = logging.getLogger("iso8601.iso8601")
logger.setLevel(logging.CRITICAL)

__author__ = "asaka <lan@leancloud.rocks>"
__version__ = "2.1.9"


__all__ = [
    "ACL",
    "Engine",
    "File",
    "FriendshipQuery",
    "GeoPoint",
    "HttpsRedirectMiddleware",
    "InboxQuery",
    "Installation",
    "LeanCloudError",
    "LeanEngineError",
    "Object",
    "Query",
    "Relation",
    "Role",
    "Status",
    "SysMessage",
    "User",
    "client",
    "cloud",
    "init",
    "push",
    "use_master_key",
    "use_production",
    "use_region",
]


version_info = sys.version_info


if version_info.major == 2 and version_info.minor < 7:
    warnings.warn("Python2 version less than 7 is not supported", LeanCloudWarning)


if version_info.minor == 3 and version_info.minor < 4:
    warnings.warn("Python3 version less than 4 is not supported", LeanCloudWarning)
