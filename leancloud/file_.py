# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re
import json
import base64
import codecs
import random

import six
import requests
from six import StringIO

import leancloud
from leancloud import client
from leancloud._compat import BytesIO
from leancloud._compat import PY2
from leancloud._compat import range_type
from leancloud._compat import file_type
from leancloud._compat import buffer_type
from leancloud.mime_type import mime_types
from leancloud.errors import LeanCloudError

__author__ = 'asaka <lan@leancloud.rocks>'


class File(object):
    def __init__(self, name, data=None, type_=None):
        self._name = name
        self.id = None
        self._url = None
        self._acl = None
        self.current_user = None  # TODO
        self._metadata = {
            'owner': 'unknown'
        }
        if self.current_user and self.current_user is not None:
            self._metadata['owner'] = self.current_user.id

        pattern = re.compile('\.([^.]*)$')
        extension = pattern.findall(name)
        if extension:
            self.extension = extension[0].lower()
        else:
            self.extension = ''

        if type_:
            self._type = type_
        else:
            self._type = mime_types.get(self.extension, 'text/plain')

        if data is None:
            self._source = None
        elif isinstance(data, BytesIO):
            self._source = data
        elif isinstance(data, file_type):
            data.seek(0, os.SEEK_SET)
            self._source = BytesIO(data.read())
        elif isinstance(data, buffer_type):
            self._source = BytesIO(data)
        elif PY2:
            import cStringIO
            if isinstance(data, cStringIO.OutputType):
                data.seek(0, os.SEEK_SET)
                self._source = BytesIO(data.getvalue())
            else:
                raise TypeError('data must be a StringIO / buffer / file instance')

        else:
            raise TypeError('data must be a StringIO / buffer / file instance')

        if self._source:
            self._source.seek(0, os.SEEK_END)
            self._metadata['size'] = self._source.tell()
            self._source.seek(0, os.SEEK_SET)

    @classmethod
    def create_with_url(cls, name, url, meta_data=None, type_=None):
        f = File(name, None, type_)
        if meta_data:
            f._metadata.update(meta_data)

        f._url = url
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

    def _save_to_qiniu(self):
        import qiniu
        output = BytesIO()
        self._source.seek(0)
        base64.encode(self._source, output)
        self._source.seek(0)
        output.seek(0)
        hex_octet = lambda: hex(int(0x10000 * (1 + random.random())))[-4:]
        key = ''.join(hex_octet() for _ in range_type(4))
        key = '{0}.{1}'.format(key, self.extension)
        data = {
            'name': self._name,
            'key': key,
            'ACL': self._acl,
            'mime_type': self._type,
            'metaData': self._metadata,
        }
        response = client.post('/qiniu', data)
        content = response.json()
        self.id = content['objectId']
        self._url = content['url']
        uptoken = content['token']
        ret, info = qiniu.put_data(uptoken, key, self._source)

        if info.status_code != 200:
            raise LeanCloudError(1, 'the file is not saved, qiniu status code: {0}'.format(info.status_code))

    def _save_to_leancloud(self):
        self._source.seek(0)
        encoded = codecs.encode(self._source.read(), 'base64')
        data = {
            'base64': encoded.decode('utf-8'),
            '_ContentType': self._type,
            'ACL': self._acl,
            'mime_type': self._type,
            'metaData': self._metadata,
        }
        response = client.post('/files/{}'.format(self._name), data)
        response.raise_for_status()
        content = response.json()
        self.id = content['objectId']
        self._url = content['url']
        self._name = content['name']

    def save(self):
        if self._source:
            if client.REGION == 'US':
                self._save_to_leancloud()
            else:
                self._save_to_qiniu()
        elif self._url and self.metadata.get('__source') == 'external':
            data = {
                'name': self._name,
                'ACL': self._acl,
                'metaData': self._metadata,
                'mime_type': self._type,
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

    def _save_external(self):
        data = {
            'name': self._name,
            'ACL': self._acl,
            'metaData': self._metadata,
            'mime_type': self._type,
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

    def _save_to_cos(self):
        hex_octet = lambda: hex(int(0x10000 * (1 + random.random())))[-4:]
        key = ''.join(hex_octet() for _ in range(4))
        key = '{0}.{1}'.format(key, self.extension)
        data = {
            'name': self._name,
            'key': key,
            'ACL': self._acl,
            'mime_type': self._type,
            'metaData': self._metadata,
        }
        response = client.post('/fileTokens', data)
        content = response.json()
        self.id = content['objectId']
        self._url = content['url']
        uptoken = content['token']
        headers = {
            'Authorization': uptoken,
        }
        self._source.seek(0)
        data = {
            'op': 'upload',
            'filecontent': self._source.read(),
        }
        response = requests.post(content['upload_url'], headers=headers, files=data)
        self._source.seek(0)
        info = response.json()
        if info['code'] != 0:
            raise LeanCloudError(1, 'this file is not saved, qcloud cos status code: {}'.format(info['code']))

    def save(self):
        if self._url and self.metadata.get('__source') == 'external':
            self._save_external()
        elif not self._source:
            pass
        elif client.APP_ID.endswith('-9Nh9j0Va'):
            self._save_to_cos()
        elif client.REGION == 'US':
            self._save_to_leancloud()
        else:
            self._save_to_qiniu()
        return self

    def fetch(self):
        response = client.get('/files/{0}'.format(self.id))
        content = response.json()
        self._name = content.get('name')
        self.id = content.get('objectId')
        self._url = content.get('url')
        self._type = content.get('mime_type')
        self._metadata = content.get('metaData')
