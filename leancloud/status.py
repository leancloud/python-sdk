# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from collections import namedtuple
from datetime import datetime

from leancloud import client
from leancloud import utils
from leancloud.query import Query
from leancloud.user import User

__author__ = "asaka"


StatusesCount = namedtuple("StatusesCount", ["total", "unread"])


class Status(object):
    def __init__(self, **data):
        self.id = None  # type: str
        self.created_at = None  # type: datetime
        self.updated_at = None  # type: datetime
        self._data = data
        self.inbox_type = "default"

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value
        return self

    def send(self, query):
        current_user = User.get_current()
        if not current_user:
            raise ValueError("Please sign in an user")

        params = {
            "inboxType": self.inbox_type,
            "data": self._data,
            "query": query.dump(),
            "source": self._data.get("source") or current_user._to_pointer(),
        }
        params["query"]["className"] = query._query_class._class_name

        content = client.post("/statuses", params=params).json()
        self.id = content["objectId"]
        self.created_at = utils.decode("createdAt", content["createdAt"])

    def send_to_followers(self):
        current_user = User.get_current()
        if not current_user:
            raise ValueError("Please sign in an user")

        query = Query("_Follower").select("follower").equal_to("user", current_user)
        self.send(query)

    def send_private_status(self, target):
        current_user = User.get_current()
        if not current_user:
            raise ValueError("Please sign in an user")

        if not isinstance(target, User):
            raise TypeError("target must be a leancloud.User")

        query = Query("User").equal_to("objectId", target.id)
        self.inbox_type = "private"
        self.send(query)

    def destroy(self):
        if not self.id:
            raise ValueError("This status is not saved")
        client.delete("/statuses/" + self.id)

    def _update_data(self, server_data):
        self.id = server_data.pop("objectId")
        self.created_at = utils.decode("createdAt", server_data.pop("createdAt"))
        self.updated_at = utils.decode("updatedAt", server_data.pop("updatedAt"))
        self._data = utils.decode(None, server_data)

    @staticmethod
    def count_unread_statuses(owner, inbox_type="default"):
        params = {
            "inboxType": inbox_type,
            "owner": utils.encode(owner),
        }
        content = client.get("/subscribe/statuses/count", params).json()
        return StatusesCount(total=content["total"], unread=content["unread"])


class InboxQuery(Query):
    def __init__(self):
        super(InboxQuery, self).__init__("_Status")
        self._since_id = 0
        self._max_id = 0
        self._inbox_type = "default"
        self._owner = None

    def since_id(self, value):
        self._since_id = value
        return self

    def max_id(self, value):
        self._max_id = value
        return self

    def owner(self, value):
        self._owner = value
        return self

    def inbox_type(self, value):
        self._inbox_type = value
        return self

    def _new_object(self):
        return Status()

    def _do_request(self, params):
        return client.get("/subscribe/statuses", params).json()

    def dump(self):
        result = super(InboxQuery, self).dump()
        result["owner"] = utils.encode(self._owner)
        result["inboxType"] = self._inbox_type
        result["sinceId"] = self._since_id
        result["maxId"] = self._max_id
        return result
