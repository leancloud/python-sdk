# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from leancloud.object_ import Object
from leancloud import client
from leancloud import utils


__author__ = 'asaka <lan@leancloud.rocks>'


class Installation(Object):
    pass


class Notification(Object):
    pass


def send(data, channels=None, push_time=None, expiration_time=None, expiration_interval=None, where=None, cql=None):
    """
    发送推送消息。返回结果为此条推送对应的 _Notification 表中的对象，但是如果需要使用其中的数据，需要调用 fetch() 方法将数据同步至本地。

    :param channels: 需要推送的频道
    :type channels: list or tuple
    :param push_time: 推送的时间
    :type push_time: datetime
    :param expiration_time: 消息过期的绝对日期时间
    :type expiration_time: datetime
    :param expiration_interval: 消息过期的相对时间，从调用 API 的时间开始算起，单位是秒
    :type expiration_interval: int
    :param where: 一个查询 _Installation 表的查询条件 leancloud.Query 对象
    :type where: leancloud.Query
    :param cql: 一个查询 _Installation 表的查询条件 CQL 语句
    :type cql: basestring
    :param data: 推送给设备的具体信息，详情查看 https://leancloud.cn/docs/push_guide.html#消息内容_Data
    :rtype: Notification
    """
    if push_time and expiration_time:
        raise TypeError('Both expiration_time and expiration_time_interval can\'t be set')
    params = {
        'data': data,
    }
    if channels:
        params['channels'] = channels
    if push_time:
        params['push_time'] = push_time.isoformat()
    if expiration_time:
        params['expiration_time'] = expiration_time.isoformat()
    if expiration_interval:
        params['expiration_interval'] = expiration_interval
    if where:
        params['where'] = where.dump().get('where', {})
    if cql:
        params['cql'] = cql

    result = utils.response_to_json(client.post('/push', params=params))

    notification = Notification.create_without_data(result['objectId'])
    return notification
