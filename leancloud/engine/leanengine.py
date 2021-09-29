# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools
import json
import logging
import sys
import traceback

import six
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotAcceptable
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.wrappers import Response

import leancloud
from . import context

__author__ = "asaka <lan@leancloud.rocks>"

logger = logging.getLogger("leancloud.cloudcode.cloudcode")

user = context.local("user")
current = context.local("current")

# http.HTTPStatus is not available in Python 2
http_status_codes = {
    100,
    101,
    102,
    200,
    201,
    202,
    203,
    204,
    205,
    206,
    207,
    208,
    226,
    300,
    301,
    302,
    303,
    304,
    305,
    307,
    308,
    400,
    401,
    402,
    403,
    404,
    405,
    406,
    407,
    408,
    409,
    410,
    411,
    412,
    413,
    414,
    415,
    416,
    417,
    421,
    422,
    423,
    424,
    426,
    428,
    429,
    431,
    451,
    500,
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    508,
    510,
    511,
}


class LeanEngineError(Exception):
    def __init__(
        self,
        code=None,  # for backward compatibility, should be 400
        message="error",  # for backward compatibility, should be required
        status=None,  # for backward compatibility, should be 400
    ):
        if status is None:
            if isinstance(code, six.string_types):
                self.message = code
                self.code = 400  # for backward compatibility, should be 1
                self.status = 400
            else:
                self.message = message
                # for backward compatibility, should be 1
                self.code = 400 if code is None else code
                self.status = self.code if self.code in http_status_codes else 400
        else:
            if isinstance(code, six.string_types):
                self.message = code
                self.code = 400
                self.status = status
            else:
                self.message = message
                self.code = 1 if code is None else code
                self.status = status


class LeanEngineApplication(object):
    def __init__(self, fetch_user):
        self.fetch_user = fetch_user
        self.url_map = Map(
            [
                Rule("/__engine/1/functions/<func_name>", endpoint="cloud_function"),
                Rule("/__engine/1.1/functions/<func_name>", endpoint="cloud_function"),
                Rule("/__engine/1/call/<func_name>", endpoint="rpc_function"),
                Rule("/__engine/1.1/call/<func_name>", endpoint="rpc_function"),
                Rule("/__engine/1/functions/BigQuery/<event>", endpoint="on_bigquery"),
                Rule(
                    "/__engine/1.1/functions/BigQuery/<event>", endpoint="on_bigquery"
                ),
                Rule("/__engine/1.1/functions/_User/onLogin", endpoint="on_login"),
                Rule("/__engine/1/functions/_User/onLogin", endpoint="on_login"),
                Rule("/__engine/1.1/functions/_User/onAuthData", endpoint="on_auth_data"),
                Rule("/__engine/1/functions/_User/onAuthData", endpoint="on_auth_data"),
                Rule(
                    "/__engine/1/functions/<class_name>/<hook_name>",
                    endpoint="cloud_hook",
                ),
                Rule(
                    "/__engine/1.1/functions/<class_name>/<hook_name>",
                    endpoint="cloud_hook",
                ),
                Rule(
                    "/__engine/1/functions/onVerified/<verify_type>",
                    endpoint="on_verified",
                ),
                Rule(
                    "/__engine/1.1/functions/onVerified/<verify_type>",
                    endpoint="on_verified",
                ),
                Rule("/__engine/1/functions/_ops/metadatas", endpoint="ops_meta_data"),
                Rule(
                    "/__engine/1.1/functions/_ops/metadatas", endpoint="ops_meta_data"
                ),
                Rule("/1/functions/<func_name>", endpoint="cloud_function"),
                Rule("/1.1/functions/<func_name>", endpoint="cloud_function"),
                Rule("/1/call/<func_name>", endpoint="rpc_function"),
                Rule("/1.1/call/<func_name>", endpoint="rpc_function"),
                Rule("/1/functions/BigQuery/<event>", endpoint="on_bigquery"),
                Rule("/1.1/functions/BigQuery/<event>", endpoint="on_bigquery"),
                Rule("/1.1/functions/_User/onLogin", endpoint="on_login"),
                Rule("/1/functions/_User/onLogin", endpoint="on_login"),
                Rule("/1.1/functions/_User/onAuthData", endpoint="on_auth_data"),
                Rule("/1/functions/_User/onAuthData", endpoint="on_auth_data"),
                Rule("/1/functions/<class_name>/<hook_name>", endpoint="cloud_hook"),
                Rule("/1.1/functions/<class_name>/<hook_name>", endpoint="cloud_hook"),
                Rule("/1/functions/onVerified/<verify_type>", endpoint="on_verified"),
                Rule("/1.1/functions/onVerified/<verify_type>", endpoint="on_verified"),
                Rule("/1/functions/_ops/metadatas", endpoint="ops_meta_data"),
                Rule("/1.1/functions/_ops/metadatas", endpoint="ops_meta_data"),
            ]
        )
        self.cloud_codes = {}

    def __call__(self, environ, start_response):
        self.process_session(environ)
        response = self.dispatch_request(environ)
        return response(environ, start_response)

    def process_session(self, environ):
        request = environ["leanengine.request"]
        context.local.current = context.Current()
        context.local.current.meta = {
            "remote_address": get_remote_address(request),
        }

        if environ["_app_params"]["session_token"] not in (None, ""):
            session_token = environ["_app_params"]["session_token"]
            if self.fetch_user:
                user = leancloud.User.become(session_token)
                context.local.current.user = user
                context.local.user = user
            context.local.current.session_token = session_token
            return

        try:
            data = json.loads(request.get_data(as_text=True))
        except ValueError:
            context.local.user = None
            return

        if "user" in data and data["user"]:
            user = leancloud.User()
            user._update_data(data["user"])
            context.local.current.user = user
            context.local.current.session_token = user.get_session_token()
            context.local.user = user
            return

        context.local.user = None

    def dispatch_request(self, environ):
        request = environ["leanengine.request"]
        app_params = environ["_app_params"]
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
        except HTTPException as e:
            return e

        params = request.get_data(as_text=True)
        values["params"] = json.loads(params) if params != "" else {}

        try:
            if endpoint == "cloud_function":
                result = {
                    "result": dispatch_cloud_func(
                        self.cloud_codes, app_params, decode_object=False, **values
                    )
                }
            elif endpoint == "rpc_function":
                result = {
                    "result": dispatch_cloud_func(
                        self.cloud_codes, app_params, decode_object=True, **values
                    )
                }
            elif endpoint == "cloud_hook":
                result = dispatch_cloud_hook(self.cloud_codes, app_params, **values)
            elif endpoint == "on_verified":
                result = {
                    "result": dispatch_on_verified(
                        self.cloud_codes, app_params, **values
                    )
                }
            elif endpoint == "on_login":
                result = {
                    "result": dispatch_on_login(self.cloud_codes, app_params, **values)
                }
            elif endpoint == "on_auth_data":
                result = {
                    "result": dispatch_on_auth_data(self.cloud_codes, app_params, **values)
                }
            elif endpoint == "ops_meta_data":
                from .authorization import MASTER_KEY

                if (
                    request.environ.get("_app_params", {}).get("master_key")
                    != MASTER_KEY
                ):
                    raise LeanEngineError(code=401, message="Unauthorized.")
                result = {"result": dispatch_ops_meta_data(self.cloud_codes)}
            elif endpoint == "on_bigquery":
                result = {
                    "result": dispatch_on_bigquery(
                        self.cloud_codes, app_params, **values
                    )
                }
            else:
                raise ValueError  # impossible
            return Response(json.dumps(result), mimetype="application/json")
        except LeanEngineError as e:
            return Response(
                json.dumps({"code": e.code, "error": e.message}),  # noqa: B306
                status=e.status,
                mimetype="application/json",
            )
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            return Response(
                json.dumps({"code": 141, "error": "Cloud Code script had an error."}),
                status=500,
                mimetype="application/json",
            )

    def update_cloud_codes(self, engine_cloud_codes):
        already_register_func_name = set(self.cloud_codes.keys()).intersection(
            set(engine_cloud_codes.keys())
        )
        if already_register_func_name:
            is_are = "is" if len(already_register_func_name) == 1 else "are"
            raise RuntimeError(
                "cloud function: {0} {1} already registerd.".format(
                    ",".join(already_register_func_name), is_are
                )
            )
        self.cloud_codes.update(engine_cloud_codes)


hook_name_mapping = {
    "beforeSave": "__before_save_for_",
    "afterSave": "__after_save_for_",
    "beforeUpdate": "__before_update_for_",
    "afterUpdate": "__after_update_for_",
    "beforeDelete": "__before_delete_for_",
    "afterDelete": "__after_delete_for_",
}

root_engine = None


def register_cloud_func(_cloud_codes, func_or_func_name):
    if isinstance(func_or_func_name, six.string_types):
        func_name = func_or_func_name

        def inner_func(func):
            if func_name in _cloud_codes:
                raise RuntimeError(
                    "cloud function: {0} is already registered".format(func_name)
                )
            _cloud_codes[func_name] = func
            return func

        return inner_func

    func = func_or_func_name
    func_name = func.__name__
    if func_name in _cloud_codes:
        raise RuntimeError(
            "cloud function: {0} is already registered".format(func_name)
        )
    _cloud_codes[func_name] = func
    return func


def dispatch_cloud_func(_cloud_codes, app_params, func_name, decode_object, params):
    # let's check realtime hook sign first
    realtime_hook_funcs = [
        "_messageReceived",
        "_receiversOffline",
        "_messageSent",
        "_messageUpdate",
        "_conversationStart",
        "_conversationStarted",
        "_conversationAdd",
        "_conversationAdded",
        "_conversationRemove",
        "_conversationRemoved",
        "_conversationUpdate",
        "_clientOnline",
        "_clientOffline",
        "_rtmClientSign",
    ]
    from .authorization import HOOK_KEY

    if func_name in realtime_hook_funcs:
        current_hook_key = app_params.get("hook_key")
        if not current_hook_key or current_hook_key != HOOK_KEY:
            raise LeanEngineError(code=401, message="Unauthorized.")

    # delete all keys in params which starts with low dash.
    # JS SDK may send it's app info with them.
    params = {
        k: v for k, v in params.items() if (not k.startswith("_")) or k == "__type"
    }

    if decode_object:
        params = leancloud.utils.decode("", params)

    func = _cloud_codes.get(func_name)
    if not func:
        raise LeanEngineError(
            code=404, message="cloud func named '{0}' not found.".format(func_name)
        )

    logger.info("{0} is called!".format(func_name))

    result = func(**params)

    if decode_object:
        result = leancloud.utils.encode(result, dump_objects=True)

    return result


def register_cloud_hook(_cloud_codes, class_name, hook_name):
    # hack the hook name
    hook_name = hook_name_mapping[hook_name] + class_name

    if hook_name in _cloud_codes:
        raise RuntimeError(
            "cloud hook {0} on class {1} is already registered".format(
                hook_name, class_name
            )
        )

    def new_func(func):
        _cloud_codes[hook_name] = func

    return new_func


before_save = functools.partial(register_cloud_hook, hook_name="beforeSave")

after_save = functools.partial(register_cloud_hook, hook_name="afterSave")

before_update = functools.partial(register_cloud_hook, hook_name="beforeUpdate")

after_update = functools.partial(register_cloud_hook, hook_name="afterUpdate")

before_delete = functools.partial(register_cloud_hook, hook_name="beforeDelete")

after_delete = functools.partial(register_cloud_hook, hook_name="afterDelete")


def dispatch_cloud_hook(_cloud_codes, app_params, class_name, hook_name, params):
    from .authorization import HOOK_KEY

    current_hook_key = app_params.get("hook_key")
    if not current_hook_key or current_hook_key != HOOK_KEY:
        raise LeanEngineError(code=401, message="Unauthorized.")
    hook_name = hook_name_mapping[hook_name] + class_name
    if hook_name not in _cloud_codes:
        raise NotAcceptable

    obj = leancloud.Object.create(class_name)
    obj._update_data(params["object"])

    if "_updatedKeys" in params["object"]:
        obj.updated_keys = params["object"]["_updatedKeys"]

    if hook_name.startswith("__before"):
        if obj.has("__before"):
            obj.set("__before", obj.get("__before"))
        else:
            obj.disable_before_hook()
    elif hook_name.startswith("__after"):
        if obj.has("__after"):
            obj.set("__after", obj.get("__after"))
        else:
            obj.disable_after_hook()

    logger.info("{0}:{1} is called!".format(class_name, hook_name))

    func = _cloud_codes[hook_name]
    if not func:
        raise leancloud.LeanEngineError(
            code=404, message="cloud hook named '{0}' not found.".format(hook_name)
        )

    func(obj)
    if hook_name.startswith("__after"):
        return {"result": "ok"}
    elif hook_name.startswith("__before_delete_for"):
        return {}
    else:
        return obj.dump()


def register_on_verified(_cloud_codes, verify_type):
    if verify_type not in set(["sms", "email"]):
        raise RuntimeError("verify_type must be sms or email")

    func_name = "__on_verified_{0}".format(verify_type)

    def new_func(func):
        if func_name in _cloud_codes:
            raise RuntimeError("on verified is already registered")
        _cloud_codes[func_name] = func

    return new_func


def dispatch_on_verified(_cloud_codes, app_params, verify_type, params):
    func_name = "__on_verified_" + verify_type
    from .authorization import HOOK_KEY

    hook_key = app_params.get("hook_key")
    if not hook_key or hook_key != HOOK_KEY:
        raise LeanEngineError(code=401, message="Unauthorized.")

    user = leancloud.User()
    user._update_data(params["object"])

    func = _cloud_codes.get(func_name)
    if not func:
        return
    return func(user)


def register_on_login(_cloud_codes, func):
    func_name = "__on_login__User"

    if func_name in _cloud_codes:
        raise RuntimeError("on login is already registered")
    _cloud_codes[func_name] = func


def dispatch_on_login(_cloud_codes, app_params, params):
    from .authorization import HOOK_KEY

    current_hook_key = app_params.get("hook_key")
    if not current_hook_key or current_hook_key != HOOK_KEY:
        raise LeanEngineError(code=401, message="Unauthorized.")

    func = _cloud_codes.get("__on_login__User")
    if not func:
        return

    user = leancloud.User()
    user._update_data(params["object"])

    return func(user)

def register_on_auth_data(_cloud_codes, func):
    func_name = "__on_authdata__User"

    if func_name in _cloud_codes:
        raise RuntimeError("on authdata is already registered")
    _cloud_codes[func_name] = func

def dispatch_on_auth_data(_cloud_codes, app_params, params):
    from .authorization import HOOK_KEY
    current_hook_key = app_params.get("hook_key")
    if not current_hook_key or current_hook_key != HOOK_KEY:
        raise LeanEngineError(code=401, message="Unauthorized.")

    func = _cloud_codes.get("__on_authdata__User")
    if not func:
        return

    auth_data = params["authData"]
    return func(auth_data)
    

def dispatch_ops_meta_data(_cloud_codes):
    return list(_cloud_codes.keys())


def register_on_bigquery(_cloud_codes, event):
    if event == "end":
        func_name = "__on_complete_bigquery_job"
    else:
        raise RuntimeError("event not support")

    def inner_func(func):
        if func_name in _cloud_codes:
            raise RuntimeError("on bigquery is already registered")
        _cloud_codes[func_name] = func

    return inner_func


def dispatch_on_bigquery(_cloud_codes, app_params, event, params):
    if event == "onComplete":
        func_name = "__on_complete_bigquery_job"
    else:
        return

    from .authorization import HOOK_KEY

    current_hook_key = app_params.get("hook_key")
    if not current_hook_key or current_hook_key != HOOK_KEY:
        raise LeanEngineError(code=401, message="Unauthorized.")

    func = _cloud_codes.get(func_name)
    if not func:
        return

    ok = True if params["status"] == "OK" else False
    return func(ok, params)


def get_remote_address(request):
    return (
        request.headers.get("x-real-ip")
        or request.headers.get("x-forwarded-for")
        or request.remote_addr
    )
