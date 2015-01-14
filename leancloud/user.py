# coding: utf-8

__author__ = 'asaka'

import leancloud
from leancloud import rest
from leancloud import Object


class User(Object):
    def __init__(self, **attrs):
        self._is_current_user = False
        self._session_token = None
        super(User, self).__init__(**attrs)

    def _merge_magic_field(self, attrs):
        self._session_token = attrs.get('sessionToken')
        attrs.pop('sessionToken', None)

        return super(User, self)._merge_magic_field(attrs)

    def sign_up(self):
        username = self.get('username')
        if not username:
            raise TypeError('invalid username: {}'.format(username))

        password = self.get('password')
        if not password:
            raise TypeError('invalid password')

        return self.save()

    def login(self):
        response = rest.get('/login', params=self.dump())
        print response.json()

    def follow(self, target_id):
        if self.id is None:
            raise ValueError('Please sign in')
        response = rest.post('/users/{}/friendship/{}'.format(self.id, target_id))
        content = response.json()
        if 'error' in content:
            raise leancloud.LeanCloudError(content['code'], content['error'])

    def unfollow(self, target_id):
        if self.id is None:
            raise ValueError('Please sign in')
        response = rest.delete('/users/{}/friendship/{}'.format(self.id, target_id))
        content = response.json()
        if 'error' in content:
            raise leancloud.LeanCloudError(content['code'], content['error'])
