# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re
import io
import hashlib
import uuid
import logging
import warnings
import threading

import requests

import leancloud
from leancloud import client
from leancloud import utils
from leancloud._compat import PY2
from leancloud._compat import string_types
from leancloud._compat import file_type
from leancloud._compat import buffer_type
from leancloud.errors import LeanCloudError
from leancloud.errors import LeanCloudWarning

__author__ = 'asaka <lan@leancloud.rocks>'

logger = logging.getLogger(__name__)


class File(object):
    _class_name = '_File'  # walks like a leancloud.Object

    def __init__(self, name='', data=None, mime_type=None, type_=None):
        self._name = name
        self.id = None
        self._url = None
        self._acl = None
        self.current_user = leancloud.User.get_current()
        self._metadata = {
            'owner': 'unknown'
        }
        if self.current_user and self.current_user != None:  # NOQA: self.current_user may be a thread_local object
            self._metadata['owner'] = self.current_user.id

        if type_ is not None:
            warnings.warn(LeanCloudWarning('optional param `type_` is deprecated, please use `mime_type` instead'))
            mime_type = type_

        pattern = re.compile('\.([^.]*)$')
        extension = pattern.findall(name)
        if extension:
            self.extension = extension[0].lower()
        else:
            self.extension = ''

        self._mime_type = mime_type

        if data is None:
            self._source = None
        elif isinstance(data, io.BytesIO):
            self._source = data
        elif isinstance(data, file_type):
            data.seek(0, os.SEEK_SET)
            self._source = io.BytesIO(data.read())
        elif isinstance(data, buffer_type):
            self._source = io.BytesIO(data)
        elif PY2:
            import cStringIO
            import StringIO
            if isinstance(data, (cStringIO.OutputType, StringIO.StringIO)):
                data.seek(0, os.SEEK_SET)
                self._source = io.BytesIO(data.getvalue())
            else:
                raise TypeError('data must be a StringIO / buffer / file instance')

        else:
            raise TypeError('data must be a StringIO / buffer / file instance')

        if self._source:
            self._source.seek(0, os.SEEK_END)
            self._metadata['size'] = self._source.tell()
            self._source.seek(0, os.SEEK_SET)
            checksum = hashlib.md5()
            checksum.update(self._source.getvalue())
            self._metadata['_checksum'] = checksum.hexdigest()

    @utils.classproperty
    def query(cls):
        return leancloud.Query(cls)

    @classmethod
    def create_with_url(cls, name, url, meta_data=None, mime_type=None, type_=None):
        if type_ is not None:
            warnings.warn('optional param `type_` is deprecated, please use `mime_type` instead')
            mime_type = type_

        f = File(name, None, mime_type)
        if meta_data:
            f._metadata.update(meta_data)

        if isinstance(url, string_types):
            f._url = url
        else:
            raise ValueError('url must be a str / unicode')

        f._metadata['__source'] = 'external'
        return f

    @classmethod
    def create_without_data(cls, object_id):
        f = File('')
        f.id = object_id
        return f

    def get_acl(self):
        return self._acl

    def set_acl(self, acl):
        if not isinstance(acl, leancloud.ACL):
            raise TypeError('acl must be a leancloud.ACL instance')
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
        return self._metadata['size']

    @property
    def owner_id(self):
        return self._metadata['owner']

    @property
    def metadata(self):
        return self._metadata

    def get_thumbnail_url(self, width, height, quality=100, scale_to_fit=True, fmt='png'):
        if not self._url:
            raise ValueError('invalid url')

        if width < 0 or height < 0:
            raise ValueError('invalid height or width params')

        if quality > 100 or quality <= 0:
            raise ValueError('quality must between 0 and 100')

        mode = 2 if scale_to_fit else 1

        return self.url + '?imageView/{0}/w/{1}/h/{2}/q/{3}/format/{4}'.format(mode, width, height, quality, fmt)

    def destroy(self):
        if not self.id:
            return False
        response = client.delete('/files/{0}'.format(self.id))
        if response.status_code != 200:
            raise LeanCloudError(1, "the file is not sucessfully destroyed")

    def _save_to_qiniu(self, token, key):
        import qiniu
        self._source.seek(0)
        ret, info = qiniu.put_data(token, key, self._source)
        self._source.seek(0)

        if info.status_code != 200:
            self._save_callback(token, False)
            raise LeanCloudError(1, 'the file is not saved, qiniu status code: {0}'.format(info.status_code))
        self._save_callback(token, True)

    def _save_to_s3(self, token, upload_url):
        self._source.seek(0)
        response = requests.put(upload_url, data=self._source.getvalue(), headers={'Content-Type': self.mime_type})
        if response.status_code != 200:
            self._save_callback(token, False)
            raise LeanCloudError(1, 'The file is not successfully saved to S3')
        self._source.seek(0)
        self._save_callback(token, True)

    def _save_external(self):
        data = {
            'name': self._name,
            'ACL': self._acl,
            'metaData': self._metadata,
            'mime_type': self.mime_type,
            'url': self._url,
        }
        response = client.post('/files/{0}'.format(self._name), data)
        content = response.json()

        self._name = content['name']
        self._url = content['url']
        self.id = content['objectId']
        if 'size' in content:
            self._metadata['size'] = content['size']
        else:
            raise ValueError

    def _save_to_qcloud(self, token, upload_url):
        headers = {
            'Authorization': token,
        }
        self._source.seek(0)
        data = {
            'op': 'upload',
            'filecontent': self._source.read(),
        }
        response = requests.post(upload_url, headers=headers, files=data)
        self._source.seek(0)
        info = response.json()
        if info['code'] != 0:
            self._save_callback(token, False)
            raise LeanCloudError(1, 'this file is not saved, qcloud cos status code: {}'.format(info['code']))
        self._save_callback(token, True)

    def _save_callback(self, token, successed):
        if not token:
            return
        def f():
            try:
                client.post('/fileCallback', {
                    'token': token,
                    'result': successed,
                })
            except LeanCloudError as e:
                logger.warning('call file callback failed, error: %s', e)
        threading.Thread(target=f).start()

    def save(self):
        if self._url and self.metadata.get('__source') == 'external':
            self._save_external()
        elif not self._source:
            pass
        else:
            content = self._get_file_token()
            self._mime_type = content['mime_type']
            if content['provider'] == 'qiniu':
                self._save_to_qiniu(content['token'], content['key'])
            elif content['provider'] == 'qcloud':
                self._save_to_qcloud(content['token'], content['upload_url'])
            elif content['provider'] == 's3':
                self._save_to_s3(content.get('token'), content['upload_url'])
            else:
                raise RuntimeError('The provider field in the fetched content is empty')
            self._update_data(content)

    def _update_data(self, server_data):
        if 'objectId' in server_data:
            self.id = server_data.get('objectId')
        if 'name' in server_data:
            self._name = server_data.get('name')
        if 'url' in server_data:
            self._url = server_data.get('url')
        if 'mime_type' in server_data:
            self._mime_type = server_data['mime_type']
        if 'metaData' in server_data:
            self._metadata = server_data.get('metaData')

    def _get_file_token(self):
        key = uuid.uuid4().hex
        if self.extension:
            key = '{0}.{1}'.format(key, self.extension)
        data = {
            'name': self._name,
            'key': key,
            'ACL': self._acl,
            'mime_type': self.mime_type,
            'metaData': self._metadata,
        }
        response = client.post('/fileTokens', data)
        content = response.json()
        self.id = content['objectId']
        self._url = content['url']
        content['key'] = key
        return content

    def fetch(self):
        response = client.get('/files/{0}'.format(self.id))
        content = response.json()
        self._update_data(content)
