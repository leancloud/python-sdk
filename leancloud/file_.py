# coding: utf-8
import os
import re
import base64
import cStringIO
import StringIO
import random

import qiniu

import leancloud
from leancloud import client
from leancloud import utils
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
        elif isinstance(data, cStringIO.OutputType):
            self._source = StringIO.StringIO(data.getvalue())
        elif isinstance(data, StringIO.StringIO):
            self._source = data
        elif isinstance(data, file):
            data.seek(0, os.SEEK_SET)
            self._source = StringIO.StringIO(data.read())
        elif isinstance(data, buffer):
            self._source = StringIO.StringIO(data)
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

    def save(self):
        if self._source:
            output = cStringIO.StringIO()
            self._source.seek(0)
            base64.encode(self._source, output)
            self._source.seek(0)
            output.seek(0)
            hex_octet = lambda: hex(int(0x10000 * (1 + random.random())))[-4:]
            key = ''.join(hex_octet() for _ in xrange(4))
            key = '{0}.{1}'.format(key, self.extension)
            data = {
                'name': self._name,
                'key': key,
                'ACL': self._acl,
                'mime_type': self._type,
                'metaData': self._metadata,
            }
            response = client.post('/qiniu', data)
            content = utils.response_to_json(response)
            self.id = content['objectId']
            self._url = content['url']
            uptoken = content['token']
            ret, info = qiniu.put_data(uptoken, key, self._source)

            if info.status_code != 200:
                raise LeanCloudError(1, 'the file is not saved, qiniu status code: {0}'.format(info.status_code))
        elif self._url and self.metadata['__source'] == 'external':
            data = {
                'name': self._name,
                'ACL': self._acl,
                'metaData': self._metadata,
                'mime_type': self._type,
                'url': self._url,
            }
            response = client.post('/files/{0}'.format(self._name), data)
            content = utils.response_to_json(response)

            self._name = content['name']
            self._url = content['url']
            self.id = content['objectId']
            if 'size' in content:
                self._metadata['size'] = content['size']
            else:
                raise ValueError

        return self
