# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import threading
from typing import Optional

import six

from leancloud import client
from leancloud.errors import LeanCloudError
from leancloud.query import FriendshipQuery
from leancloud.object_ import Object
from leancloud.relation import Relation

__author__ = 'asaka'


thread_locals = threading.local()
thread_locals.current_user = None


class User(Object):
    def __init__(self, **attrs):
        self._session_token = None
        super(User, self).__init__(**attrs)

    def get_session_token(self):
        return self._session_token

    @property
    def session_token(self):
        return self._session_token

    def _merge_metadata(self, attrs):
        if 'sessionToken' in attrs:
            self._session_token = attrs.pop('sessionToken')

        return super(User, self)._merge_metadata(attrs)

    @classmethod
    def create_follower_query(cls, user_id):
        if not user_id or not isinstance(user_id, six.string_types):
            raise TypeError('invalid user_id: {0}'.format(user_id))
        query = FriendshipQuery('_Follower')
        query.equal_to('user', User.create_without_data(user_id))
        return query

    @classmethod
    def create_followee_query(cls, user_id):
        if not user_id or not isinstance(user_id, six.string_types):
            raise TypeError('invalid user_id: {0}'.format(user_id))
        query = FriendshipQuery('_Followee')
        query.equal_to('user', User.create_without_data(user_id))
        return query

    @classmethod
    def get_current(cls):  # type: () -> Optional[User]
        return getattr(thread_locals, 'current_user', None)

    @classmethod
    def set_current(cls, user):
        thread_locals.current_user = user

    @classmethod
    def become(cls, session_token):
        """
        通过 session token 获取用户对象

        :param session_token: 用户的 session token
        :return: leancloud.User
        """
        response = client.get('/users/me', params={'session_token': session_token})
        content = response.json()
        user = cls()
        user._update_data(content)
        user._handle_save_result(True)
        if 'smsCode' not in content:
            user._attributes.pop('smsCode', None)
        return user

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
        keys = list(auth_data.keys())
        for key in keys:
            if not auth_data[key]:
                del auth_data[key]

    def _handle_save_result(self, make_current=False):
        if make_current:
            User.set_current(self)
        self._cleanup_auth_data()
        # self._sync_all_auth_data()
        self._attributes.pop('password', None)

    def save(self, make_current=False):
        super(User, self).save()
        self._handle_save_result(make_current)

    def sign_up(self, username=None, password=None):
        """
        创建一个新用户。新创建的 User 对象，应该使用此方法来将数据保存至服务器，而不是使用 save 方法。
        用户对象上必须包含 username 和 password 两个字段
        """
        if username:
            self.set('username', username)
        if password:
            self.set('password', password)

        username = self.get('username')
        if not username:
            raise TypeError('invalid username: {0}'.format(username))
        password = self.get('password')
        if not password:
            raise TypeError('invalid password')

        self.save(make_current=True)

    def login(self, username=None, password=None, email=None):
        """
        登录用户。成功登录后，服务器会返回用户的 sessionToken 。

        :param username: 用户名
        :param email: 邮箱地址（username 和 email 这两个参数必须传入一个且仅能传入一个）
        :param password: 用户密码
        """
        if username:
            self.set('username', username)
        if password:
            self.set('password', password)
        if email:
            self.set('email', email)
        # 同时传入 username、email、password 的情况下，这三个字段会一起发给后端。
        # 这时后端会忽略 email，等价于只传 username 和 password。
        # 这里的 login 函数的实现依赖后端的这一行为，没有校验 username 和 email 中调用者传入且仅传入了其中一个参数。
        response = client.post('/login', params=self.dump())
        content = response.json()
        self._update_data(content)
        self._handle_save_result(True)
        if 'smsCode' not in content:
            self._attributes.pop('smsCode', None)

    def logout(self):
        if not self.is_current:
            return
        self._cleanup_auth_data()
        del thread_locals.current_user

    @classmethod
    def login_with_mobile_phone(cls, phone_number, password):
        user = User()
        params = {
            'mobilePhoneNumber': phone_number,
            'password': password
        }
        user._update_data(params)
        user.login()
        return user

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

    @classmethod
    def login_with(cls, platform, third_party_auth_data):
        '''
        把第三方平台号绑定到 User 上

        ：param platform: 第三方平台名称 base string
        '''
        user = User()
        return user.link_with(platform, third_party_auth_data)

    def link_with(self, provider, third_party_auth_data):
        if type(provider) != str:
            raise TypeError('input should be a string')
        auth_data = self.get('authData')
        if not auth_data:
            auth_data = {}
        auth_data[provider] = third_party_auth_data
        self.set('authData', auth_data)
        self.save()
        self._handle_save_result(True)
        return self

    def unlink_from(self, provider):
        '''
        解绑特定第三方平台
        '''
        if type(provider) != str:
            raise TypeError('input should be a string')
        self.link_with(provider, None)
        # self._sync_auth_data(provider)
        return self

    def is_linked(self, provider):
        try:
            self.get('authData')[provider]
        except KeyError:
            return False
        return True

    @classmethod
    def signup_or_login_with_mobile_phone(cls, phone_number, sms_code):
        '''
        param phone_nubmer: string_types
        param sms_code: string_types

        在调用此方法前请先使用 request_sms_code 请求 sms code
        '''
        data = {
            'mobilePhoneNumber': phone_number,
            'smsCode': sms_code
        }
        response = client.post('/usersByMobilePhone', data)
        content = response.json()
        user = cls()
        user._update_data(content)
        user._handle_save_result(True)
        if 'smsCode' not in content:
            user._attributes.pop('smsCode', None)
        return user

    def update_password(self, old_password, new_password):
        route = '/users/' + self.id + '/updatePassword'
        params = {
            'old_password': old_password,
            'new_password': new_password
        }
        content = client.put(route, params).json()
        self._update_data(content)
        self._handle_save_result(True)

    def get_username(self):
        return self.get('username')

    def get_mobile_phone_number(self):
        return self.get('mobilePhoneNumber')

    def set_mobile_phone_number(self, phone_number):
        return self.set('mobilePhoneNumber', phone_number)

    def set_username(self, username):
        return self.set('username', username)

    def set_password(self, password):
        return self.set('password', password)

    def set_email(self, email):
        return self.set('email', email)

    def get_email(self):
        return self.get('email')

    def get_roles(self):
        return Relation.reverse_query('_Role', 'users', self).find()

    def refresh_session_token(self):
        """
        重置当前用户 `session token`。
        会使其他客户端已登录用户登录失效。
        """
        response = client.put('/users/{}/refreshSessionToken'.format(self.id), None)
        content = response.json()
        self._update_data(content)
        self._handle_save_result(False)

    def is_authenticated(self):
        '''
        判断当前用户对象是否已登录。
        会先检查此用户对象上是否有 `session_token`，如果有的话，会继续请求服务器验证 `session_token` 是否合法。
        '''
        session_token = self.get_session_token()
        if not session_token:
            return False
        try:
            response = client.get('/users/me', params={'session_token': session_token})
        except LeanCloudError as e:
            if e.code == 211:
                return False
            else:
                raise
        return response.status_code == 200

    @classmethod
    def request_password_reset(self, email):
        params = {'email': email}
        client.post('/requestPasswordReset', params)

    @classmethod
    def request_email_verify(self, email):
        params = {'email': email}
        client.post('/requestEmailVerify', params)

    @classmethod
    def request_mobile_phone_verify(cls, phone_number, validate_token=None):
        params = {'mobilePhoneNumber': phone_number}
        if validate_token is not None:
            params['validate_token'] = validate_token
        client.post('/requestMobilePhoneVerify', params)

    @classmethod
    def request_password_reset_by_sms_code(cls, phone_number, validate_token=None):
        params = {'mobilePhoneNumber': phone_number}
        if validate_token is not None:
            params['validate_token'] = validate_token
        client.post('/requestPasswordResetBySmsCode', params)

    @classmethod
    def reset_password_by_sms_code(cls, sms_code, new_password):
        params = {'password': new_password}
        client.put("/resetPasswordBySmsCode/" + sms_code, params)

    @classmethod
    def verify_mobile_phone_number(cls, sms_code):
        client.post('/verfyMobilePhone/' + sms_code, {})

    @classmethod
    def request_login_sms_code(cls, phone_number, validate_token=None):
        params = {'mobilePhoneNumber': phone_number}
        if validate_token is not None:
            params['validate_token'] = validate_token
        client.post('/requestLoginSmsCode', params)
