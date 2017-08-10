# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

import six

import leancloud

__author__ = 'asaka <lan@leancloud.rocks>'


class Role(leancloud.Object):
    def __init__(self, name=None, acl=None):
        super(Role, self).__init__()
        if name:
            self.set_name(name)
        if acl is None:
            acl = leancloud.ACL()
            acl.set_public_read_access(True)
        self.set_acl(acl)

    @property
    def name(self):
        return self.get('name')

    @name.setter
    def name(self, name):
        return self.set('name', name)

    def get_name(self):
        """
        获取 Role 的 name，等同于 role.get('name')
        """
        return self.get('name')

    def set_name(self, name):
        """
        为 Role 设置 name，等同于 role.set('name', name)
        """
        return self.set('name', name)

    @property
    def users(self):
        return self.relation('users')

    def get_users(self):
        """
        获取当前 Role 下所有绑定的用户。
        """
        return self.relation('users')

    @property
    def roles(self):
        return self.relation('roles')

    def get_roles(self):
        return self.relation('roles')

    def validate(self, attrs):
        if 'name' in attrs and attrs['name'] != self.get_name():
            new_name = attrs['name']
            if not isinstance(new_name, six.string_types):
                raise TypeError('role name must be string_types')
            r = re.compile('^[0-9a-zA-Z\-_]+$')
            if not r.match(new_name):
                raise TypeError('role\'s name can only contain alphanumeric characters, _, -, and spaces.')

        return super(Role, self).validate(attrs)
