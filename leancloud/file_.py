# coding: utf-8

import os
import re
import cStringIO
import StringIO

import leancloud
from leancloud.mine_type import mine_types


__author__ = 'asaka <lan@leancloud.rocks>'


class File(object):
    def __init__(self, name, data=None, type_=None):
        self._name = name
        self.id = None
        self._url = None
        self._acl = None
        self.current_user = None  # TODO
        self._meta_data = {
            'owner': 'unknown'
        }
        if self.current_user and self.current_user is not None:
            self._meta_data['owner'] = self.current_user.id

        pattern = re.compile('\.([^.]*)$')
        extension = pattern.findall(name)
        if extension:
            extension = extension[0].lower()
        else:
            extension = None

        if type_:
            self._guessed_type = type_
        else:
            self._guessed_type = mine_types.get(extension, 'text/plain')

        if data is None:
            # self._source = cStringIO.StringIO()
            self._source = None
        elif isinstance(data, (cStringIO.OutputType, StringIO.StringIO)):
            self._source = data
        elif isinstance(data, file):
            data.seek(0, os.SEEK_SET)
            self._source = cStringIO.StringIO(data.read())
        elif isinstance(data, buffer):
            self._source = cStringIO.StringIO(data)
        else:
            raise TypeError('data must be a StringIO / buffer / file instance')

        if self._source:
            self._source.seek(0, os.SEEK_END)
            self._meta_data['size'] = self._source.tell()
            self._source.seek(0, os.SEEK_SET)

    @classmethod
    def create_with_url(cls, name, url, meta_data=None, type_=None):
        f = File(name, None, type_)
        if meta_data:
            f._meta_data.update(meta_data)

        f._url = url
        f._meta_data['__source'] = 'external'
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