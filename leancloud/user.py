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

    @property
    def is_current(self):
        return self._is_current_user

    def _cleanup_auth_data(self):
        if not self.is_current:
            return
        auth_data = self.get('authData')
        if not auth_data:
            return
        keys = auth_data.keys()
        for key in keys:
            if not auth_data[key]:
                del auth_data[key]

    def _sync_all_auth_data(self):
        auth_data = self.get('authData')
        if not auth_data:
            return
        for key in auth_data.keys():
            self._sync_auth_data(key)

    def _sync_auth_data(self, key):
        if not self.is_current:
            return

    def _handle_save_result(self, make_current=False):
        if make_current:
            self._is_current_user = True
        self._cleanup_auth_data()
        self._sync_all_auth_data()
        self._server_data.pop('password', None)
        self._rebuild_estimated_data_for_key('password')

    def save(self):
        super(User, self).save()
        self._handle_save_result(False)

    def sign_up(self):
        username = self.get('username')
        if not username:
            raise TypeError('invalid username: {}'.format(username))

        password = self.get('password')
        if not password:
            raise TypeError('invalid password')

        self.save()

    def login(self):
        response = rest.get('/login', params=self.dump())
        content = response.json()
        server_data = self.parse(content, response.status_code)
        self._finish_fetch(server_data)
        self._handle_save_result(True)
        if 'smsCode' not in server_data:
            self.attributes.pop('smsCode', None)

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
