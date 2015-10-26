# coding: utf-8

import leancloud
from leancloud import utils


__author__ = 'asaka <lan@leancloud.rocks>'


def run(_cloud_func_name, **params):
    """
    调用 LeanEngine 上的远程代码

    :param name: 需要调用的远程 Cloud Code 的名称
    :type name: basestring
    :param params: 调用参数
    :return: 调用结果
    """
    response = leancloud.client.post('/functions/{0}'.format(_cloud_func_name), params=params)
    content = utils.response_to_json(response)
    return utils.decode(None, content)['result']


def request_sms_code(phone_number, idd='+86', sms_type='sms', template=None, params=None):
    """
    请求发送手机验证码

    :param phone_number: 需要验证的手机号码
    :param idd: 号码的所在地国家代码，默认为中国（+86）
    :param sms_type: 验证码发送方式，'voice' 为语音，'sms' 为短信
    :return: None
    """
    if not isinstance(phone_number, basestring):
        raise TypeError('phone_number must be a string')

    data = {
        'mobilePhoneNumber': phone_number,
        'smsType': sms_type,
        'IDD': idd,
    }

    if template is not None:
        params['template'] = template

    if params is not None:
        data.update(params)

    leancloud.client.post('/requestSmsCode', params=data)


def verify_sms_code(phone_number, code):
    """
    获取到手机验证码之后，验证验证码是否正确。如果验证失败，抛出异常。

    :param phone_number: 需要验证的手机号码
    :param code: 接受到的验证码
    :return: None
    """
    params = {
        'mobilePhoneNumber': phone_number,
    }
    leancloud.client.post('/verifySmsCode/{0}'.format(code), params=params)
    return True
