# coding: utf-8

import leancloud
from leancloud import utils


__author__ = 'asaka <lan@leancloud.rocks>'


def run(name, **params):
    """
    调用 LeanEngine 上的原生代码

    :param name: 需要调用的远程 Cloud Code 的名称
    :type name: basestring
    :param params: 调用参数
    :return: 调用结果
    """
    response = leancloud.client.post('/functions/{0}'.format(name), params=params)
    content = utils.response_to_json(response)
    return utils.decode(None, content)['result']
