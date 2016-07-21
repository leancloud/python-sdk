# coding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abc 
from datetime import datetime
import six

import leancloud
from leancloud import File as AVFile
from leancloud import Object
from leancloud import relation
from leancloud import user
from leancloud._compat import with_metaclass
from leancloud import acl


class Field(with_metaclass(abc.ABCMeta)):
    def __init__(self, default=None, nullable=True, verifier=None):
        self.default = default
        self.nullable = nullable
        self.verifier = verifier

    @abc.abstractmethod
    def validate(self, value):
        return

    def verifier_helper(self, value):
        if not self.verifier:
            pass
        else:
            if not callable(self.verifier):
                raise ValueError("field verifier should be a function")
            self.verifier(value)

    def is_valid_empty_field(self, value):
        if self.nullable and value == None:
            return True
        return False

    def validate_helper(self, value, type_list):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, type_list):
                raise ValueError('This field requires {0}, but {1} is {2}'.format(type_list, value, type(value)))
            self.verifier_helper(value)


class Number(Field):
    def __init__(self, default=None, nullable=True, verifier=None):
        super(Number, self).__init__(default, nullable, verifier)

    def validate(self, value):
        if six.PY2:
            self.validate_helper(value, (float, int, long))
        else:
            self.validate_helper(value, (float, int))


class Array(Field):
    def __init__(self, default=None, nullable=True, verifier=None):
        super(Array, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self.validate_helper(value, list)


class Date(Field):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(Date, self).__init__(default, nullable, verifier)
    
    def validate(self, value):
        self.validate_helper(value, datetime)


class ACL(Field):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(ACL, self).__init__(default, nullable, verifier)
    
    def validate(self, value):
        self.validate_helper(value, acl.ACL)


class String(Field):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(String, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self.validate_helper(value, str)


class Boolean(Field):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(Boolean, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self.validate_helper(value, bool)

class File(Field):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(File, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self.validate_helper(value, AVFile)


class Pointer(Field):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(Pointer, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self.validate_helper(value, (Object, leancloud.models.model.Model))


class User(Field):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(User, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self.validate_helper(value, (user.User, leancloud.models.model.UserModel))


class Relation(Field):
    def  __init__(self, default=None, nullable=True, verifier=None):
        super(Relation, self).__init__(default, nullable, verifier)

    def validate(self, value):
        self.validate_helper(value, relation.Relation)
