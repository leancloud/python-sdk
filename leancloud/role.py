# coding: utf-8

import re

import leancloud

__author__ = 'asaka <lan@leancloud.rocks>'


class Role(leancloud.Object):
    def __init__(self, name, acl):
        super(Role, self).__init__()
        self.set_name(name)
        self.set_acl(acl)

    def get_name(self):
        return self.get('name')

    def set_name(self, name):
        return self.set('name', name)

    def get_users(self):
        return self.relation('users')

    def get_roles(self):
        return self.relation('roles')

    def validate(self, attrs):
        if 'name' in attrs and attrs['name'] != self.get_name():
            new_name = attrs['name']
            if not isinstance(new_name, basestring):
                raise TypeError('role name must be a basestring')
            r = re.compile('^[0-9a-zA-Z\-_]+$')
            if not r.match(new_name):
                raise TypeError('role\'s name can only contain alphanumeric characters, _, -, and spaces.')

        return super(Role, self).validate(attrs)
