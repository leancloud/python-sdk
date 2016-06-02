# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import leancloud
from leancloud._compat import string_types

__author__ = 'asaka <lan@leancloud.rocks>'


PUBLIC_KEY = '*'


class ACL(object):
    def __init__(self, permissions_by_id=None):
        self.permissions_by_id = permissions_by_id or {}

    def dump(self):
        return self.permissions_by_id

    def _set_access(self, access_type, user_id, allowed):
        if isinstance(user_id, leancloud.User):
            user_id = user_id.id
        elif isinstance(user_id, leancloud.Role):
            user_id = 'role:' + user_id.get_name()
        permissions = self.permissions_by_id.get(user_id)
        if permissions is None:
            if not allowed:
                return
            permissions = {}
            self.permissions_by_id[user_id] = permissions

        if allowed:
            self.permissions_by_id[user_id][access_type] = True
        else:
            del self.permissions_by_id[user_id][access_type]
            if not self.permissions_by_id[user_id]:
                del self.permissions_by_id[user_id]

    def _get_access(self, access_type, user_id):
        if isinstance(user_id, leancloud.User):
            user_id = user_id.id
        elif isinstance(user_id, leancloud.Role):
            user_id = 'role:' + user_id.get_name()
        permissions = self.permissions_by_id.get(user_id)
        if not permissions:
            return False
        return permissions.get(access_type, False)

    def set_read_access(self, user_id, allowed):
        return self._set_access('read', user_id, allowed)

    def get_read_access(self, user_id):
        return self._get_access('read', user_id)

    def set_write_access(self, user_id, allowed):
        return self._set_access('write', user_id, allowed)

    def get_write_access(self, user_id):
        return self._get_access('write', user_id)

    def set_public_read_access(self, allowed):
        return self.set_read_access(PUBLIC_KEY, allowed)

    def get_public_read_access(self):
        return self.get_read_access(PUBLIC_KEY)

    def set_public_write_access(self, allowed):
        return self.set_write_access(PUBLIC_KEY, allowed)

    def get_public_write_access(self):
        return self.get_write_access(PUBLIC_KEY)

    def set_role_read_access(self, role, allowed):
        if isinstance(role, leancloud.Role):
            role = role.get_name()
        if not isinstance(role, string_types):
            raise TypeError('role must be a leancloud.Role or str')
        self.set_read_access('role:{0}'.format(role), allowed)

    def get_role_read_access(self, role):
        if isinstance(role, leancloud.Role):
            role = role.get_name()
        if not isinstance(role, string_types):
            raise TypeError('role must be a leancloud.Role or str')
        return self.get_read_access('role:{0}'.format(role))

    def set_role_write_access(self, role, allowed):
        if isinstance(role, leancloud.Role):
            role = role.get_name()
        if not isinstance(role, string_types):
            raise TypeError('role must be a leancloud.Role or str')
        self.set_write_access('role:{0}'.format(role), allowed)

    def get_role_write_access(self, role):
        if isinstance(role, leancloud.Role):
            role = role.get_name()
        if not isinstance(role, string_types):
            raise TypeError('role must be a leancloud.Role or str')
        return self.get_write_access('role:{0}'.format(role))
