import leancloud
from leancloud.acl import ACL

from typing import Dict


class Role(object):
    def __init__(self, name: str=None, acl: ACL=None) -> None:...

    def get_name(self):...

    def set_name(self):...

    def get_users(self):...

    def get_roles(self):...

    def validat(self, attrs: Dict):...
