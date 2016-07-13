import abc 
from datetime import datetime

import leancloud
from leancloud import File as AVFile
from leancloud import Object
from leancloud import relation
from leancloud import user
from leancloud._compat import with_metaclass
from leancloud import acl


class Field(with_metaclass(abc.ABCMeta)):
    def __init__(self, default=None, nullable=True, verifier=NotImplemented):
        self.default = default
        self.nullable = nullable
        self.verifier = verifier

    @abc.abstractmethod
    def validate(self, value):
        return

    def is_valid_empty_field(self, value):
        if self.nullable and value == None:
            return True
        return False


class Number(Field):
    def __init__(self, default=None, nullable=True, verifier=NotImplemented):
        super(Number, self).__init__(default, nullable, verifier)
    def validate(self, value):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, (float, int)):
                raise ValueError('NumField requires a value of float or int')


class Array(Field):
    def __init__(self, default=None, nullable=True, verifier=NotImplemented):
        super(Array, self).__init__(default, nullable, verifier)

    def validate(self, value):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, list):
                raise ValueError('Array Field requires the value of list type')


class Date(Field):
    def  __init__(self, default=None, nullable=True, verifier=NotImplemented):
        super(Date, self).__init__(default, nullable, verifier)
    
    def validate(self, value):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, datetime):
                raise ValueError('Datetime field requires the value of datetime.datetime type, while {0} is of {1} type'.format(value, type(value)))


class ACL(Field):
    def  __init__(self, default=None, nullable=True, verifier=NotImplemented):
        super(ACL, self).__init__(default, nullable, verifier)
    
    def validate(self, value):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, acl.ACL):
                raise ValueError('ACL Field requires the value of Leancloud.acl type')


class String(Field):
    def  __init__(self, default=None, nullable=True, verifier=NotImplemented):
        super(String, self).__init__(default, nullable, verifier)

    def validate(self, value):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, str):
                raise ValueError('String Field requires the value of str type, but {0} has a type of {1}'.format(value, type(value)))


class Boolean(Field):
    def  __init__(self, default=None, nullable=True, verifier=NotImplemented):
        super(Boolean, self).__init__(default, nullable, verifier)

    def validate(self, value):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, bool):
                raise ValueError('Boolean Field requires the value of bool type, but {0} has a type of {1}'.format(value, type(value)))

class File(Field):
    def  __init__(self, default=None, nullable=True, verifier=NotImplemented):
        super(File, self).__init__(default, nullable, verifier)

    def validate(self, value):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, AVFile):
                raise ValueError('File field requires the value of Leancloud.File type, but {0} has a type of {1}'.format(value, type(value)))


class Pointer(Field):
    def  __init__(self, default=None, nullable=True, verifier=NotImplemented):
        Object, leancloud.models.model.Model()
        super(Pointer, self).__init__(default, nullable, verifier)

    def validate(self, value):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, (Object, leancloud.models.model.Model)):
                raise ValueError('Pointer field requires the value of Leancloud.Object or Leancloud.Model type, but {0} has a type of {1}'.format(value, type(value)))


class User(Field):
    def  __init__(self, default=None, nullable=True, verifier=NotImplemented):
        super(User, self).__init__(default, nullable, verifier)

    def validate(self, value):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, (user.User, leancloud.models.model.UserModel)):
                raise ValueError('User field requires the value of Leancloud.User type, but {0} has a type of {1}'.format(value, type(value)))


class Relation(Field):
    def  __init__(self, default=None, nullable=True, verifier=NotImplemented):
        super(Relation, self).__init__(default, nullable, verifier)

    def validate(self, value):
        if not self.is_valid_empty_field(value):
            if not isinstance(value, relation.Relation):
                raise ValueError('Relation field requires the value of Leancloud.Relation type, but {0} has a type of {1}'.format(value, type(value)))
