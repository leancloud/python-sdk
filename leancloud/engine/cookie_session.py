# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from werkzeug import http
from werkzeug.wrappers import Request
from secure_cookie.cookie import SecureCookie

from . import utils
from leancloud.user import User


__author__ = "asaka <lan@leancloud.rocks>"


class CookieSessionMiddleware(object):
    """
    用来在 webhosting 功能中实现自动管理 LeanCloud 用户登录状态的 WSGI 中间件。
    使用此中间件之后，在处理 web 请求中调用了 `leancloud.User.login()` 方法登录成功后，
    会将此用户 session token 写入到 cookie 中。
    后续此次会话都可以通过 `leancloud.User.get_current()` 获取到此用户对象。

    :param secret: 对保存在 cookie 中的用户 session token 进行签名时需要的 key，可使用任意方法随机生成，请不要泄漏
    :type secret: str
    :param name: 在 cookie 中保存的 session token 的 key 的名称，默认为 "leancloud:session"
    :type name: str
    :param excluded_paths:
           指定哪些 URL path 不处理 session token，比如在处理静态文件的 URL path 上不进行处理，防止无谓的性能浪费
    :type excluded_paths: list
    :param fetch_user: 处理请求时是否要从存储服务获取用户数据，
           如果为 false 的话，
           leancloud.User.get_current() 获取到的用户数据上除了 session_token 之外没有任何其他数据，
           需要自己调用 fetch() 来获取。
           为 true 的话，会自动在用户对象上调用 fetch()，这样将会产生一次数据存储的 API 调用。
           默认为 false
    :type fetch_user: bool
    :param expires: 设置 cookie 的 expires
    :type expires: int or datetime
    :param max_age: 设置 cookie 的 max_age，单位为秒
    :type max_age: int
    """

    def __init__(
        self,
        app,
        secret,
        name="leancloud:session",
        excluded_paths=None,
        fetch_user=False,
        expires=None,
        max_age=None,
    ):
        if not secret:
            raise RuntimeError("secret is required")
        self.fetch_user = fetch_user
        self.secret = secret
        self.app = app
        self.name = name
        self.excluded_paths = [
            "/__engine/",
            "/1/functions/",
            "/1.1/functions/",
            "/1/call/",
            "/1.1/call/",
        ]
        self.expires = expires
        self.max_age = max_age
        if excluded_paths:
            self.excluded_paths += excluded_paths

    def __call__(self, environ, start_response):
        self.pre_process(environ)

        def new_start_response(status, response_headers, exc_info=None):
            self.post_process(environ, response_headers)
            return start_response(status, response_headers, exc_info)

        return self.app(environ, new_start_response)

    def pre_process(self, environ):
        request = Request(environ)
        for prefix in self.excluded_paths:
            if request.path.startswith(prefix):
                return

        cookie = request.cookies.get(self.name)
        if not cookie:
            return

        session = SecureCookie.unserialize(cookie, self.secret)

        if "session_token" not in session:
            return

        if not self.fetch_user:
            user = User()
            user._session_token = session["session_token"]
            user.id = session["uid"]
            User.set_current(user)
        else:
            user = User.become(session["session_token"])
            User.set_current(user)

    def post_process(self, environ, headers):
        user = User.get_current()
        if not user:
            cookies = http.parse_cookie(environ)
            if self.name in cookies:
                raw = http.dump_cookie(self.name, "", expires=1)
                headers.append((utils.to_native("Set-Cookie"), raw))
            return
        cookie = SecureCookie(
            {"uid": user.id, "session_token": user.get_session_token()}, self.secret
        )
        raw = http.dump_cookie(
            self.name, cookie.serialize(), expires=self.expires, max_age=self.max_age
        )
        headers.append((utils.to_native("Set-Cookie"), raw))
