# coding: utf-8

__author__ = 'asaka'

from leancloud import rest
from leancloud import Object


class User(Object):
    def __init__(self):
        self._is_current_user = False
        self._session_token = None
        super(User, self).__init__()

    def _merge_magic_field(self, attrs):
        self._session_token = attrs.get('sessionToken')
        attrs.pop('sessionToken')

        return super(User, self)._merge_magic_field(attrs)

    def sign_up(self, username, password, attrs):
        if not username:
            raise TypeError('invalid username: {}'.format(username))

        if not password:
            raise TypeError('invalid password')

        self.set(attrs)

        return self.save()

    def log_in(self):
        response = rest.get('/login', params=self.dump())
        print response
