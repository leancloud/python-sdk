# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six

import leancloud
from leancloud import utils
from leancloud.engine import leanengine


__author__ = "asaka <lan@leancloud.rocks>"


def run(_cloud_func_name, **params):
    """
    调用 LeanEngine 上的远程代码
    :param name: 需要调用的远程 Cloud Code 的名称
    :type name: string_types
    :param params: 调用参数
    :return: 调用结果
    """
    response = leancloud.client.post(
        "/functions/{0}".format(_cloud_func_name), params=params
    )
    content = response.json()
    return utils.decode(None, content)["result"]


def _run_in_local(_cloud_func_name, **params):
    if not leanengine.root_engine:
        return
    result = leanengine.dispatch_cloud_func(
        leanengine.root_engine.app.cloud_codes, {}, _cloud_func_name, False, params
    )
    return utils.decode(None, result)


run.remote = run
run.local = _run_in_local


def rpc(_cloud_rpc_name, **params):
    """
    调用 LeanEngine 上的远程代码
    与 cloud.run 类似，但是允许传入 leancloud.Object 作为参数，也允许传入 leancloud.Object 作为结果
    :param name: 需要调用的远程 Cloud Code 的名称
    :type name: basestring
    :param params: 调用参数
    :return: 调用结果
    """
    encoded_params = {}
    for key, value in params.items():
        if isinstance(params, leancloud.Object):
            encoded_params[key] = utils.encode(value._dump())
        else:
            encoded_params[key] = utils.encode(value)
    response = leancloud.client.post(
        "/call/{}".format(_cloud_rpc_name), params=encoded_params
    )
    content = response.json()
    return utils.decode(None, content["result"])


def _rpc_in_local(_cloud_rpc_name, **params):
    if not leanengine.root_engine:
        return
    result = leanengine.dispatch_cloud_func(
        leanengine.root_engine.app.cloud_codes, {}, _cloud_rpc_name, True, params
    )
    return utils.decode(None, result)


rpc.remote = rpc
rpc.local = _rpc_in_local


def request_sms_code(
    phone_number,
    idd="+86",
    sms_type="sms",
    validate_token=None,
    template=None,
    sign=None,
    params=None,
):
    """
    请求发送手机验证码
    :param phone_number: 需要验证的手机号码
    :param idd: 号码的所在地国家代码，默认为中国（+86）
    :param sms_type: 验证码发送方式，'voice' 为语音，'sms' 为短信
    :param template: 模版名称
    :param sign: 短信签名名称
    :return: None
    """
    if not isinstance(phone_number, six.string_types):
        raise TypeError("phone_number must be a string")

    data = {
        "mobilePhoneNumber": phone_number
        if phone_number.startswith("+")
        else idd + phone_number,
        "smsType": sms_type,
    }

    if template is not None:
        data["template"] = template

    if sign is not None:
        data["sign"] = sign

    if validate_token is not None:
        data["validate_token"] = validate_token

    if params is not None:
        data.update(params)

    leancloud.client.post("/requestSmsCode", params=data)


def verify_sms_code(phone_number, code):
    """
    获取到手机验证码之后，验证验证码是否正确。如果验证失败，抛出异常。
    :param phone_number: 需要验证的手机号码
    :param code: 接受到的验证码
    :return: None
    """
    params = {
        "mobilePhoneNumber": phone_number,
    }
    leancloud.client.post("/verifySmsCode/{0}".format(code), params=params)
    return True


class Captcha(object):
    """
    表示图形验证码
    """

    def __init__(self, token, url):
        self.token = token
        self.url = url

    def verify(self, code):
        """
        验证用户输入与图形验证码是否匹配
        :params code: 用户填写的验证码
        """
        return verify_captcha(code, self.token)


def request_captcha(size=None, width=None, height=None, ttl=None):
    """
    请求生成新的图形验证码
    :return: Captcha
    """
    params = {
        "size": size,
        "width": width,
        "height": height,
        "ttl": ttl,
    }
    params = {k: v for k, v in params.items() if v is not None}

    response = leancloud.client.get("/requestCaptcha", params)
    content = response.json()
    return Captcha(content["captcha_token"], content["captcha_url"])


def verify_captcha(code, token):
    """
    验证用户输入与图形验证码是否匹配
    :params code: 用户填写的验证码
    :params token: 图形验证码对应的 token
    :return: validate token
    """
    params = {
        "captcha_token": token,
        "captcha_code": code,
    }
    response = leancloud.client.post("/verifyCaptcha", params)
    return response.json()["validate_token"]


def get_server_time():
    return leancloud.client.get_server_time()
