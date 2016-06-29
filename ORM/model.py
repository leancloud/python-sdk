import six
import json
import iso8601
import warnings

import leancloud
from leancloud import client

import field


# TODO inherience
class BaseModel(type):
    def __new__(cls, name, bases, attrs):
        attrs['fields']= {field_name: f for field_name, f in attrs.items() if isinstance(f, field.Field)}
        for field_name in attrs['fields']:
            attrs.pop(field_name)
        attrs['_class_name'] = name
        return super(BaseModel, cls).__new__(cls, name, bases, attrs)

class Model(six.with_metaclass(BaseModel)):
    def __init__(self, **kargv):
        self._object = leancloud._object.Object()
        for key in kargv:
            if not key in self.fields:
                raise AttributeError('There is no {} field in the model'.format(key))
            setattr(self, key, kargv[key])

    def in_class_setattr(self, key, value):
        object.__setattr__(self, key, value)

    def in_class_delattr(self, name):
        object.__delattr__(self, name)

    def __setattr__(self, name, value):
        if name in self.fields:
            self.fields[name].verify(value)
            self.object.set(name, value)
        else:
            warnings.warn('There the value is not set to a field', leancloud.errors.LeanCloudWarning)
            self.in_class_setattr(name, value)

    def __delattr__(self, name):
        if name in self.fields:
            self._object.unset(name)
        else:
            self.in_class_delattr(name)

    def __getattr__(self, name):
        try:
            return self._object._attribute[name]
        except KeyError:
            raise AttributeError('{0} does not have the attribute {1}'.format(self.name, name))

    def increment(self, attr, num=1):
        if attr in self.fields:
            if not isinstance(self.fields[attr], field.Number):
                raise TypeError("only number can be incremented")
            else:
                self._object.increment(attr, num)
        else:
            raise AttributeError('There is no {} field in the model'.format(attr))


    def save(self, where=None, fetch_when_save=False):
        self._object.fetch_when_ave = fetch_when_save
        self._object.save(where=where)

#    def fetch(self):
#        if not self.id:
#            raise ValueError('the Model needs its ID to fetch data from the server') 
