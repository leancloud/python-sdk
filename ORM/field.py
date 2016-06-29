import abc 
import six
from datetime import datetime

from leancloud import operation
from leancloud import acl

class Field(six.with_metaclass(abc.ABCMeta)):
    def __init__(self, default=None, nullable=NotImplemented, verifier=NotImplemented):
        if default:
            self.current = operation.Set(default)
        else:
            self.current = None
        self.verifier = verifier

    @abc.abstractmethod
    def verify(self, value):
        return

#    def set_value(self, value):
#        self.validate(value)
#        self.current = operation.Set(value)
#
#    def del_field(self):
#        self.current = operation.Unset()._merge(self.current)
        

class Number(Field):
    def __init__(self, default=None, nullable=NotImplemented, verifier=NotImplemented):
        super(Number, self).__init__(default, nullable, verifier)

    def verify(self, value):
        if not (isinstance(value, float) or isinstance(value, int)):
            raise ValueError('NumField requires a value of float or int')


class List(Field):
    def __init__(self, default=None, nullable=NotImplemented, verifier=NotImplemented):
        super(List, self).__init__(default, nullable, verifier)

    def verify(self, value):
        if not isinstance(value, list):
            raise ValueError('ListField requires the value of list type')

#    def add(self, value):
#        self.current = operation.Add()._merge(self.current)
#
#    def add_unique(self, value):
#        self.current = operation.AddUnique()._merge(self.current)

class Date(Field):
    def  __init__(self, default=None, nullable=NotImplemented, verifier=NotImplemented):
        super(Date, self).__init__(default, nullable, verifier)
    
    def verify(self, value):
        if not isinstance(value, datetime):
            raise ValueError('DatetimeField requires the value of list type')

#class Acl(Field):
#    def  __init__(self, default=None, nullable=NotImplemented, verifier=NotImplemented):
#        super(Date, self).__init__(default, nullable, verifier)
#    
#    def verify(self, value):
#        if not isinstance(value, acl.ACL):
#            raise ValueError('ACL Field requires the value of Leancloud.acl type')

