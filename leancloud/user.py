# coding: utf-8

import threading

from leancloud import FriendshipQuery
from leancloud import client
from leancloud import Object
from leancloud import utils

__author__ = 'asaka'


thread_locals = threading.local()
thread_locals.current_user = None


class User(Object):
    def __init__(self, **attrs):
        self._session_token = None
        super(User, self).__init__(**attrs)

    def _merge_magic_field(self, attrs):
        self._session_token = attrs.get('sessionToken')
        attrs.pop('sessionToken', None)

        return super(User, self)._merge_magic_field(attrs)

    @classmethod
    def create_follower_query(cls, user_id):
        if not user_id or not isinstance(user_id, basestring):
            raise TypeError('invalid user_id: {0}'.format(user_id))
        query = FriendshipQuery('_Follower')
        query.equal_to('user', User.create_without_data(user_id))
        return query

    @classmethod
    def create_followee_query(cls, user_id):
        if not user_id or not isinstance(user_id, basestring):
            raise TypeError('invalid user_id: {0}'.format(user_id))
        query = FriendshipQuery('_Followee')
        query.equal_to('user', User.create_without_data(user_id))
        return query

    @classmethod
    def get_current(cls):
        return getattr(thread_locals, 'current_user', None)

    @property
    def is_current(self):
        if not getattr(thread_locals, 'current_user', None):
            return False
        return self.id == thread_locals.current_user.id

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
            thread_locals.current_user = self
        self._cleanup_auth_data()
        self._sync_all_auth_data()
        self._server_data.pop('password', None)
        self._rebuild_estimated_data_for_key('password')

    def save(self):
        super(User, self).save()
        self._handle_save_result(False)

    def sign_up(self):
        """
        创建一个新用户。新创建的 User 对象，应该使用此方法来将数据保存至服务器，而不是使用 save 方法。
        用户对象上必须包含 username 和 password 两个字段
        """
        username = self.get('username')
        if not username:
            raise TypeError('invalid username: {0}'.format(username))

        password = self.get('password')
        if not password:
            raise TypeError('invalid password')

        self.save()

    def login(self, username=None, password=None):
        """
        登陆用户。如果用户名和密码正确，服务器会返回用户的 sessionToken 。
        """
        if username:
            self.set('username', username)
        if password:
            self.set('password', password)
        response = client.get('/login', params=self.dump())
        content = utils.response_to_json(response)
        server_data = self.parse(content, response.status_code)
        self._finish_fetch(server_data, False)
        self._handle_save_result(True)
        if 'smsCode' not in server_data:
            self.attributes.pop('smsCode', None)

    def follow(self, target_id):
        """
        关注一个用户。

        :param target_id: 需要关注的用户的 id
        """
        if self.id is None:
            raise ValueError('Please sign in')
        response = client.post('/users/{0}/friendship/{1}'.format(self.id, target_id), None)
        assert response.ok

    def unfollow(self, target_id):
        """
        取消关注一个用户。

        :param target_id: 需要关注的用户的 id
        :return:
        """
        if self.id is None:
            raise ValueError('Please sign in')
        response = client.delete('/users/{0}/friendship/{1}'.format(self.id, target_id), None)
        assert response.ok
