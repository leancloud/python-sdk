
import leancloud
from .._compat import with_metaclass
import six

import field


# TODO inherience
class BaseModel(type):
    def __new__(cls, name, bases, attrs):
        attrs['fields']= {field_name: f for field_name, f in attrs.items() if isinstance(f, field.Field)}
        for field_name in attrs['fields']:
            attrs.pop(field_name)
        attrs['_object'] = leancloud.object_.Object()
        return super(BaseModel, cls).__new__(cls, name, bases, attrs)

class Model(six.with_metaclass(BaseModel)):
    def __init__(self, **kargv):
        self.id = None
        self.created_at = None
        self.updated_at = None

        self._object = leancloud.object_.Object()
        # self.__dict__['_object'] = leancloud.object_.Object()

        for key in kargv:
            if not key in self.fields:
                raise AttributeError('There is no {} field in the model'.format(key))
        for key in self.fields:
            if key in kargv:
                setattr(self, key, kargv[key])
            else:
                setattr(self, key, self.fields[key].default)

    def _inclass_setattr(self, key, value):
        object.__setattr__(self, key, value)

    def _inclass_delattr(self, name):
        object.__delattr__(self, name)

    def __setattr__(self, name, value):
        if name in self.fields:
            self.fields[name].verify(value)
            self._object.set(name, value)
        else:
            self._inclass_setattr(name, value)

    def __delattr__(self, name):
        if name in self.fields:
            self._object.unset(name)
        else:
            self._inclass_delattr(name)

    def __getattr__(self, name):
        if not self._object:
            object.__getattribute__(name)
        elif not self._object.has(name):
            raise AttributeError('The model instance does not have the attribute {}'.format(name))
        else:
            return self._object.get(name)
    
    def increment(self, attr, num=1):
        if attr in self.fields:
            if not isinstance(self.fields[attr], field.Number):
                raise TypeError("only number can be incremented")
            else:
                self._object.increment(attr, num)
        else:
            raise AttributeError('There is no {} field in the model'.format(attr))


    def save(self, where=None, fetch_when_save=False):
        self._object.fetch_when_save = fetch_when_save
        #self._object.save(where=where)
        self._object.save()
        self._copy_meta_data()

    def _copy_meta_data(self):
        for attr in ('id', 'created_at', 'updated_at'):
            if not getattr(self, attr):
                setattr(self, attr, getattr(self._object, attr))

    def fetch(self):
        if not self._object.id:
            raise ValueError('the Model needs its ID to fetch data from the server') 
        self._object.fetch()
        # self._copy_meta_data()

    def dump(self):
        return self._object.dump()

    def add(self, attr, objs):
        if attr in self.fields:
            if not isinstance(self.fields[attr], field.List):
                raise TypeError("only list can add items")
            else:
                self._object.add(attr, list(objs))
        else:
            raise AttributeError('There is no {} field in the model'.format(attr))


    def add_unique(self, attr, objs):
        if attr in self.fields:
            if not isinstance(self.fields[attr], field.List):
                raise TypeError("only list can uniquely add items")
            else:
                self._object.add_unique(attr, list(objs))
        else:
            raise AttributeError('There is no {} field in the model'.format(attr))

    def clear(self):
        self._object.clear()

    def destroy(self, value):
        self._object.destroy()

#    def destroy_all(self):
#        pass

#    def create_without_data(self, id):
#        pass

    def is_modified(self, attr=None):
        self._object.is_dirty(attr)

#    def save_all(self, objs):
#        pass

    def validate(self):
        self._object.validate(None)

class UserModel(Model):
    def __init__(self, **kargv):
        super(self, UserModel).__init__(**kargv)

    def __getattr__(self, name):
        if not self._object.has(name):
            try:
                self._object.getattr(name)
            except AttributeError:
                raise AttributeError('The model instance does not have the attribute {}'.format(name))
        else:
            return self._object.get(name)
