# coding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import leancloud
from leancloud import Object
from leancloud._compat import with_metaclass
from leancloud.models.fields import *
from leancloud import User


# TODO inherience
class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelMeta, cls).__new__
        flattened_bases = cls._get_all_bases(bases)
        hierachy_bases = flattened_bases[::-1]
        meta = {
            'abstract': False,
            'delete_rule': None,
            'allow_inherence': False,
        }
        # merge ancestors' meta
        for base in hierachy_bases:
            if hasattr(base, '_meta'):
                meta.update(base._meta)

        # merge user-defeined metadata
        meta.update(attrs.get('meta', {}))
        if 'meta' in attrs:
            del attrs['meta']
        attrs['_meta'] = meta

        # find parent class
        ancestors = [a for a in flattened_bases if type(a) == ModelMeta]
        parent = None if not ancestors else ancestors[0]

        # abstract class check
        if meta.get('abstract'):
            if parent and not parent._meta.get('abstract', False):
                raise ValueError('abstract Model should inherent from abstract models')

        # inherent fields
        fields = {}
        for base in hierachy_bases:
            if hasattr(base, '_fields'):
                fields.update(base._fields)

        # get new-added fields
        field_names = {}
        for key, value in attrs.items():
            if not isinstance(value, BaseField):
                continue
            if not value.db_field:
                value.db_field = key
            fields[key] = value

            field_names[value.db_field] = field_names.get(value.db_field, 0) + 1

        # count duplicated fields
        duplicated_fields = [k for k, v in field_names.items() if v >= 3]
        if duplicated_fields:
            raise KeyError('The following field names are duplicated: {}'.format(', '.join(duplicated_fields)))

        attrs['_fields'] = fields

        # attrs['_db_field_map'] = {field.db_field : key, field for field in fields.items}
        # attrs['_reverse_db_field_map'] = {value : key for key, value in attrs['_db_field_map'].items()}

        # attrs['_fields']['ACL'] = ACLField(default=None)

        attrs['_fields_ordered'] = tuple(
            i[1] for i in sorted(
                (value.creation_counter, value.db_field)
                for key, value in fields.items())
        )

        # handle delete rule

        return super_new(cls, name, bases, attrs)

    @classmethod
    def _get_all_bases(cls, bases):
        if not bases or bases == (object,):
            return ()
        bases = cls._get_bases_helper(bases)
        seen = []
        unique_bases = (base for base in bases if not (base in seen or seen.append(base)))
        return tuple(unique_bases)

    @classmethod
    def _get_bases_helper(cls, bases):
        for base in bases:
            if base is object:
                continue
            yield base
            for father_base in cls._get_bases_helper(base.__bases__):
                yield father_base


class Model(with_metaclass(ModelMeta)):
    def __init__(self, *arg, **kwargs):
        self._object = Object()
        self._object._class_name = self.__class__.__name__
        if arg:
            for i in range(len(arg)):
                field = self._fields_ordered[i]
                if field in kwargs:
                    raise KeyError(' multiassignment for field {}'.format(field))
                kwargs[field] = arg[i]

        for key in kwargs:
            if key not in self._fields:
                raise AttributeError('There is no {} field in the model'.format(key))
        for key in self._fields:
            if key in kwargs:
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, self._fields[key].default)

    def __iter__(self):
        return iter(self._fields_ordered)

    def __getitem__(self, name):
        try:
            if name in self._fields_ordered:
                return getattr(self, name)
        except AttributeError:
            pass
        raise KeyError(name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __contains__(self, name):
        try:
            val = getattr(self, name)
            return val is not None
        except AttributeError:
            return False

    def __len__(self):
        return len(self._fields)

    def __eq__(self, other):
        if not isinstance(other, Model):
            return False
        if not self.id:
            return self is other
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def _inclass_setattr(self, key, value):
        object.__setattr__(self, key, value)

    def _inclass_delattr(self, name):
        object.__delattr__(self, name)

    def __setattr__(self, name, value):
        if name in self._fields:
            self._fields[name].validate(value)
            self._object.set(name, value)
        else:
            # self._inclass_setattr(name, value)
            super(Model, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in self._fields:
            self._object.unset(name)
        else:
            # self._inclass_delattr(name)
            super(Model, self).__delattr__(name)

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

    def fetch_when_save(self):
        pass

    Magic_mode = False

    def increment(self, attr, num=1):
        if attr in self._fields:
            if not isinstance(self._fields[attr], NumberField):
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
#        self._object.fetch()field.
#
#    def dump(self):
#        return self._object.dump()

    def add(self, attr, objs):
        if attr in self._fields:
            if not isinstance(self._fields[attr], ListField):
                raise TypeError("only list can add items")
            else:
                self._object.add(attr, list(objs))
        else:
            raise AttributeError('There is no {} field in the model'.format(attr))

    def add_unique(self, attr, objs):
        if attr in self._fields:
            if not isinstance(self._fields[attr], ListField):
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
    def __init__(self, **kwargs):
        # maybe only validate and but not define them here? to straight up field-ordered
        self._fields['username'] = StringField()
        self._fields['password'] = StringField()

        self._object = User()
        self._object._class_name = self.__class__.__name__

        for key in kwargs:
            if key not in self._fields:
                raise AttributeError('There is no {} field in the model'.format(key))
        for key in self._fields:
            if key in kwargs:
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, self._fields[key].default)

#    def __getattr__(self, name):
#        if self._object.has(name):
#            return self._object.get(name)
#        else:
#            try:
#                print('getattr id is ', getattr(self._object, name))
#                return getattr(self._object, name)
#            except AttributeError:
#                raise AttributeError('The model instance does not have the attribute {}'.format(name))
