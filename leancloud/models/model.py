import leancloud
from leancloud import Object
from leancloud._compat import with_metaclass
from leancloud.models import field
from leancloud import User


# TODO inherience
class BaseModel(type):
    def __new__(cls, name, bases, attrs):
        attrs['fields']= {field_name: f for field_name, f in attrs.items() if isinstance(f, field.Field)}
        for field_name in attrs['fields']:
            attrs.pop(field_name)
        attrs['fields']['ACL'] = field.ACL(default=None)
        return super(BaseModel, cls).__new__(cls, name, bases, attrs)

class Model(with_metaclass(BaseModel)):
    def __init__(self, **kargv):
        self._object = Object()
        self._object._class_name = self.__class__.__name__
        # self.id = None
        # self.created_at = None
        # self.updated_at = None

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
            self.fields[name].validate(value)
            self._object.set(name, value)
        else:
            self._inclass_setattr(name, value)

    def __delattr__(self, name):
        if name in self.fields:
            self._object.unset(name)
        else:
            self._inclass_delattr(name)

#    def __getattr__(self, name):
#        # if not self._object:
#        #     object.__getattribute__(name)
#        if not self._object.has(name):
#            raise AttributeError('The model instance does not have the attribute {}'.format(name))
#        else:
#            return self._object.get(name)

    def __getattr__(self, name):
        if self._object.has(name):
            return self._object.get(name)
        else:
            try:
                return getattr(self._object, name)
            except AttributeError:
                raise AttributeError('The model instance does not have the attribute {}'.format(name))
    
    def increment(self, attr, num=1):
        if attr in self.fields:
            if not isinstance(self.fields[attr], field.Number):
                raise TypeError("only number can be incremented")
            else:
                self._object.increment(attr, num)
        else:
            raise AttributeError('There is no {} field in the model'.format(attr))


#    def save(self, where=None, fetch_when_save=False):
#        self._object.fetch_when_save = fetch_when_save
#        #self._object.save(where=where)
#        self._object.save()
#        #self._copy_meta_data()
#
#    def _copy_meta_data(self):
#        for attr in ('id', 'created_at', 'updated_at'):
#            if not getattr(self, attr):
#                setattr(self, attr, getattr(self._object, attr))
#
#    def fetch(self):
#        if not self._object.id:
#            raise ValueError('the Model needs its ID to fetch data from the server') 
#        self._object.fetch()
#
#    def dump(self):
#        return self._object.dump()

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

#    def clear(self):
#        self._object.clear()
#
#    def destroy(self, value):
#        self._object.destroy()
#
#    def destroy_all(self):
#        pass
#
#    def create_without_data(self, id):
#        pass
#
#    def is_modified(self, attr=None):
#        self._object.is_dirty(attr)
#
#    def save_all(self, objs):
#        pass
#
#    def validate(self):
#        self._object.validate(None)

class UserModel(Model):
    def __init__(self, **kargv):
        self.fields['username'] = field.String()
        self.fields['password'] = field.String()

        self._object = User()
        self._object._class_name = self.__class__.__name__

        for key in kargv:
            if not key in self.fields:
                raise AttributeError('There is no {} field in the model'.format(key))
        for key in self.fields:
            if key in kargv:
                setattr(self, key, kargv[key])
            else:
                setattr(self, key, self.fields[key].default)

#    def __getattr__(self, name):
#        if self._object.has(name):
#            return self._object.get(name)
#        else:
#            try:
#                print('getattr id is ', getattr(self._object, name))
#                return getattr(self._object, name)
#            except AttributeError:
#                raise AttributeError('The model instance does not have the attribute {}'.format(name))
