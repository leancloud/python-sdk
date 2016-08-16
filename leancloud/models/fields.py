# coding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
import six

import leancloud
from leancloud import File as AVFile
from leancloud import Object
from leancloud import relation
from leancloud import user
from leancloud import acl


class BaseField(object):
    def __init__(self, db_field=None, unnique=NotImplemented, unique_with=NotImplemented, default=None, nullable=True, verifier=None):
        self.db_field = db_field
        self.default = default
        self.nullable = nullable
        self.verifier = verifier

    def validate(self, value):
        return

    def is_valid_empty_field(self, value):
        if self.nullable and value == None:
            return True
        return False

    def _validate(self, value, type_list):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, type_list):
                raise ValueError('{0} requires {1}, but {2} is {3}'.format(self.db_field, type_list, value, type(value)))
        # verfy the value
        if self.verifier:
            if not callable(self.verifier):
                raise ValueError("field verifier should be a function")
            self.verifier(value)

    # descriptor definition of field
    def __get__(self, instance, owner):
        if instance is None:
            return self
        # return instance._data.get(self.name)

    def __set__(self, instance, value):
        pass

# TODO __init__ and Super paramerters with **karg
class NumberField(BaseField):
    def __init__(self, default=None, nullable=True, verifier=None):
        super(NumberField, self).__init__(default=default, nullable=nullable, verifier=verifier)

    def validate(self, value):
        if six.PY2:
            self._validate(value, (float, int, long))
        else:
            self._validate(value, (float, int))


class ArrayField(BaseField):
    def __init__(self, default=None, nullable=True, verifier=None):
        super(ArrayField, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self._validate(value, list)


class DateField(BaseField):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(DateField, self).__init__(default, nullable, verifier)
    
    def validate(self, value):
        self._validate(value, datetime)


class ACLField(BaseField):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(ACLField, self).__init__(default, nullable, verifier)
    
    def validate(self, value):
        self._validate(value, acl.ACL)


class StringField(BaseField):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(StringField, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self._validate(value, str)


class BooleanField(BaseField):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(BooleanField, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self._validate(value, bool)

class FileField(BaseField):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(FileField, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self._validate(value, AVFile)


class PointerField(BaseField):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(PointerField, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self._validate(value, (Object, leancloud.models.models.Model))


class UserField(BaseField):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(UserField, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self._validate(value, (user.User, leancloud.models.models.UserModel))


class RelationField(BaseField):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(RelationField, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self._validate(value, relation.Relation)
