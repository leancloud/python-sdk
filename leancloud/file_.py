# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import io
import hashlib
import logging
import threading

import six
import requests

import leancloud
from leancloud import client
from leancloud import utils
from leancloud.errors import LeanCloudError

__author__ = "asaka <lan@leancloud.rocks>"

logger = logging.getLogger(__name__)


DEFAULT_TIMEOUT = 30


class File(object):
    _class_name = "_File"  # walks like a leancloud.Object

    def __init__(self, name="", data=None, mime_type=None):
        self._name = name
        self.key = None
        self.id = None
        self._url = None
        self._acl = None
        self.current_user = leancloud.User.get_current()
        self.timeout = 30
        self._metadata = {"owner": "unknown"}
        if (
            self.current_user and self.current_user != None
        ):  # NOQA: self.current_user may be a thread_local object
            self._metadata["owner"] = self.current_user.id

        pattern = re.compile(r"\.([^.]*)$")
        extension = pattern.findall(name)
        if extension:
            self.extension = extension[0].lower()
        else:
            self.extension = ""

        self._mime_type = mime_type

        if data is None:
            self._source = None
            return

        try:
            data.read
            data.tell
            data.seek(0, os.SEEK_END)
            data.seek(0, os.SEEK_SET)
        except Exception:
            if (six.PY3 and isinstance(data, (memoryview, bytes))) or (
                six.PY2 and isinstance(data, (buffer, memoryview, str))  # noqa: F821
            ):
                data = io.BytesIO(data)
            elif data.read:
                data = io.BytesIO(data.read())
            else:
                raise TypeError(
                    "Do not know how to handle data, accepts file like object or bytes"
                )

        data.seek(0, os.SEEK_SET)
        checksum = hashlib.md5()
        while True:
            chunk = data.read(4096)
            if not chunk:
                break

            try:
                checksum.update(chunk)
            except TypeError:
                checksum.update(chunk.encode("utf-8"))

        self._metadata["_checksum"] = checksum.hexdigest()
        self._metadata["size"] = data.tell()

        # 3.5MB, 1Mbps * 30s
        # increase timeout
        if self._metadata["size"] > 3750000:
            self.timeout = self.timeout * int(self._metadata["size"] / 3750000)

        data.seek(0, os.SEEK_SET)

        self._source = data

    @utils.classproperty
    def query(self):
        return leancloud.Query(self)

    @classmethod
    def create_with_url(cls, name, url, meta_data=None, mime_type=None):
        f = File(name, None, mime_type)
        if meta_data:
            f._metadata.update(meta_data)

        if isinstance(url, six.string_types):
            f._url = url
        else:
            raise ValueError("url must be a str / unicode")

        f._metadata["__source"] = "external"
        return f

    @classmethod
    def create_without_data(cls, object_id):
        f = File("")
        f.id = object_id
        return f

    def get_acl(self):
        return self._acl

    def set_acl(self, acl):
        if not isinstance(acl, leancloud.ACL):
            raise TypeError("acl must be a leancloud.ACL instance")
        self._acl = acl

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def mime_type(self):
        return self._mime_type

    @mime_type.setter
    def set_mime_type(self, mime_type):
        self._mime_type = mime_type

    @property
    def size(self):
        return self._metadata["size"]

    @property
    def owner_id(self):
        return self._metadata["owner"]

    @property
    def metadata(self):
        return self._metadata

    def get_thumbnail_url(
        self, width, height, quality=100, scale_to_fit=True, fmt="png"
    ):
        if not self._url:
            raise ValueError("invalid url")

        if width < 0 or height < 0:
            raise ValueError("invalid height or width params")

        if quality > 100 or quality <= 0:
            raise ValueError("quality must between 0 and 100")

        mode = 2 if scale_to_fit else 1

        return self.url + "?imageView/{0}/w/{1}/h/{2}/q/{3}/format/{4}".format(
            mode, width, height, quality, fmt
        )

    def destroy(self):
        if not self.id:
            return False
        response = client.delete("/files/{0}".format(self.id))
        if response.status_code != 200:
            raise LeanCloudError(1, "the file is not sucessfully destroyed")


    def _save_to_qiniu(self, token, key):
        self._source.seek(0)

        import qiniu

        qiniu.set_default(connection_timeout=self.timeout)
        ret, info = qiniu.put_data(token, key, self._source)
        self._source.seek(0)

        if info.status_code != 200:
            self._save_callback(token, False)
            raise LeanCloudError(
                1,
                "the file is not saved, qiniu status code: {0}".format(
                    info.status_code
                ),
            )
        self._save_callback(token, True)

    def _save_to_s3(self, token, upload_url):
        self._source.seek(0)
        response = requests.put(
            upload_url, data=self._source, headers={"Content-Type": self.mime_type}
        )
        if response.status_code != 200:
            self._save_callback(token, False)
            raise LeanCloudError(1, "The file is not successfully saved to S3")
        self._source.seek(0)
        self._save_callback(token, True)

    def _save_external(self):
        data = {
            "name": self._name,
            "ACL": self._acl,
            "metaData": self._metadata,
            "mime_type": self.mime_type,
            "url": self._url,
        }
        response = client.post("/files".format(self._name), data)
        content = response.json()
        self.id = content["objectId"]

    def _save_to_qcloud(self, token, upload_url):
        headers = {
            "Authorization": token,
        }
        self._source.seek(0)
        data = {
            "op": "upload",
            "filecontent": self._source.read(),
        }
        response = requests.post(upload_url, headers=headers, files=data)
        self._source.seek(0)
        info = response.json()
        if info["code"] != 0:
            self._save_callback(token, False)
            raise LeanCloudError(
                1,
                "this file is not saved, qcloud cos status code: {}".format(
                    info["code"]
                ),
            )
        self._save_callback(token, True)

    def _save_callback(self, token, successed):
        if not token:
            return

        def f():
            try:
                client.post("/fileCallback", {"token": token, "result": successed})
            except LeanCloudError as e:
                logger.warning("call file callback failed, error: %s", e)

        threading.Thread(target=f).start()

    def save(self):
        if self._url and self.metadata.get("__source") == "external":
            self._save_external()
        elif not self._source:
            pass
        else:
            content = self._get_file_token()
            self._mime_type = content["mime_type"]
            if content["provider"] == "qiniu":
                self._save_to_qiniu(content["token"], content["key"])
            elif content["provider"] == "qcloud":
                self._save_to_qcloud(content["token"], content["upload_url"])
            elif content["provider"] == "s3":
                self._save_to_s3(content.get("token"), content["upload_url"])
            else:
                raise RuntimeError("The provider field in the fetched content is empty")
            self._update_data(content)

    def _update_data(self, server_data):
        if "objectId" in server_data:
            self.id = server_data.get("objectId")
        if "name" in server_data:
            self._name = server_data.get("name")
        if "url" in server_data:
            self._url = server_data.get("url")
        if "mime_type" in server_data:
            self._mime_type = server_data["mime_type"]
        if "metaData" in server_data:
            self._metadata = server_data.get("metaData")

    def _get_file_token(self):
        data = {
            "name": self._name,
            "ACL": self._acl,
            "mime_type": self.mime_type,
            "metaData": self._metadata,
        }
        if self.key is not None:
            data["key"] = self.key
        response = client.post("/fileTokens", data)
        content = response.json()
        self.id = content["objectId"]
        self._url = content["url"]
        self.key = content["key"]
        return content

    def fetch(self):
        response = client.get("/files/{0}".format(self.id))
        content = response.json()
        self._update_data(content)
