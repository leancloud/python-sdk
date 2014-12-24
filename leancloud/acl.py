# coding: utf-8

import leancloud.settings

__author__ = 'asaka <lan@leancloud.rocks>'


PUBLIC_KEY = '*'


class ACL(object):
    def __init__(self, permissions_by_id=None):
        self.permissions_by_id = permissions_by_id or {}

    def dump(self):
        return self.permissions_by_id

    def _set_access(self, access_type, user_id, allowed):
        # TODO: User
        # TODO: Role
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
        # TODO: USer
        # TODO: Role
        permissions = self.permissions_by_id[user_id]
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
        pass  # TODO

    def get_role_read_access(self, role):
        pass  # TODO

    def set_role_write_access(self, role, allowed):
        pass  # TODO

    def get_role_write_access(self, role):
        pass  # TODO