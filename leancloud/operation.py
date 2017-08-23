# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy

import leancloud
import leancloud.utils

__author__ = 'asaka <lan@leancloud.rocks>'


class BaseOp(object):
    def dump(self):
        raise NotImplementedError

    def _merge(self, previous):
        raise NotImplementedError

    def _apply(self, old, obj=None, key=None):
        raise NotImplementedError


_UNSET = BaseOp()


class Set(BaseOp):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def dump(self):
        return leancloud.utils.encode(self.value)

    def _merge(self, previous):
        return self

    def _apply(self, old, obj=None, key=None):
        return self.value


class Unset(BaseOp):
    def __init__(self):
        pass

    def dump(self):
        return {
            '__op': 'Delete'
        }

    def _merge(self, previous):
        return self

    def _apply(self, old, obj=None, key=None):
        return _UNSET


class Increment(BaseOp):
    def __init__(self, amount=1):
        self._amount = amount

    @property
    def amount(self):
        return self._amount

    def dump(self):
        return {
            '__op': 'Increment',
            'amount': self.amount,
        }

    def _merge(self, previous):
        if not previous:
            return self
        elif isinstance(previous, Unset):
            return Set(self.amount)
        elif isinstance(previous, Set):
            return Set(previous.value + self.amount)
        elif isinstance(previous, Increment):
            return Increment(self.amount + previous.amount)
        raise TypeError('invalid op')

    def _apply(self, old, obj=None, key=None):
        if not old:
            return self.amount
        return old + self.amount


class BitAnd(BaseOp):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def dump(self):
        return {
            '__op': 'BitAnd',
            'value': self.value,
        }

    def _merge(self, previous):
        if not previous:
            return self
        if isinstance(previous, Unset):
            return Set(0)
        if isinstance(previous, Set):
            return Set(previous.value & self.value)
        raise TypeError('invalid op')

    def _apply(self, old, obj=None, key=None):
        return old & self.value


class BitOr(BaseOp):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def dump(self):
        return {
            '__op': 'BitOr',
            'value': self.value,
        }

    def _merge(self, previous):
        if not previous:
            return self
        if isinstance(previous, Unset):
            return Set(self.value)
        if isinstance(previous, Set):
            return Set(previous.value | self.value)
        raise TypeError('invalid op')

    def _apply(self, old, obj=None, key=None):
        return old | self.value


class BitXor(BaseOp):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def dump(self):
        return {
            '__op': 'BitXor',
            'value': self.value,
        }

    def _merge(self, previous):
        if not previous:
            return self
        if isinstance(previous, Unset):
            return Set(self.value)
        if isinstance(previous, Set):
            return Set(previous.value ^ self.value)
        raise TypeError('invalid op')

    def _apply(self, old, obj=None, key=None):
        return old ^ self.value


class Add(BaseOp):
    def __init__(self, objects):
        if not isinstance(objects, (list, tuple)):
            raise TypeError('Add op requires list or tuple as parameters')
        self._objects = objects

    @property
    def objects(self):
        return self._objects

    def dump(self):
        return {
            '__op': 'Add',
            'objects': leancloud.utils.encode(self.objects),
        }

    def _merge(self, previous):
        if not previous:
            return self
        elif isinstance(previous, Unset):
            return Set(self.objects)
        elif isinstance(previous, Set):
            return Set(self._apply(previous.value))
        elif isinstance(previous, Add):
            return Add(previous.objects + self.objects)
        raise TypeError('invalid op')

    def _apply(self, old, obj=None, key=None):
        if not old:
            return self.objects
        return old + self.objects


class AddUnique(BaseOp):
    def __init__(self, objects):
        if not isinstance(objects, (list, tuple)):
            raise TypeError('op.AddUnique requires list or tuple as parameters')
        self._objects = list(set(objects))

    @property
    def objects(self):
        return self._objects

    def dump(self):
        return {
            '__op': 'AddUnique',
            'objects': leancloud.utils.encode(self.objects),
        }

    def _merge(self, previous):
        if not previous:
            return self
        elif isinstance(previous, Unset):
            return Set(self.objects)
        elif isinstance(previous, Set):
            return Set(self._apply(previous.value))
        elif isinstance(previous, AddUnique):
            return AddUnique(self._apply(previous.objects))
        raise TypeError('invalid op')

    def _apply(self, old, obj=None, key=None):
        if not old:
            return copy.deepcopy(self.objects)
        new = copy.deepcopy(old)
        # TODO: more readable
        for obj in self.objects:
            if isinstance(obj, leancloud.Object) and obj.id is not None:
                for index, another_obj in enumerate(new):
                    if another_obj.id == obj.id:
                        new[index] = obj
                        continue
                else:
                    new.append(obj)
            elif obj not in new:
                new.append(obj)
        return new


class Remove(BaseOp):
    def __init__(self, objects):
        if not isinstance(objects, (list, tuple)):
            raise TypeError('op.Remove requires list or tuple as parameters')
        self._objects = list(set(objects))

    @property
    def objects(self):
        return self._objects

    def dump(self):
        return {
            '__op': 'Remove',
            'objects': leancloud.utils.encode(self.objects)
        }

    def _merge(self, previous):
        if not previous:
            return self
        elif isinstance(previous, Unset):
            return previous
        elif isinstance(previous, Set):
            return Set(self._apply(previous.value))
        elif isinstance(previous, Remove):
            return Remove(list(set(self.objects + previous.objects)))
        raise TypeError('invalid op')

    def _apply(self, old, obj=None, key=None):
        if not old:
            return []
        new = list(set(old) - set(self.objects))
        for obj in self.objects:
            if isinstance(obj, leancloud.Object) and obj.id:
                new = [x for x in new if not (isinstance(x, leancloud.Object) and x.id == obj.id)]
        return new


class Relation(BaseOp):
    def __init__(self, adds, removes):
        self._target_class_name = None

        self.relations_to_add = set([self._pointer_to_id(x) for x in adds])
        self.relations_to_remove = set([self._pointer_to_id(x) for x in removes])

    def _pointer_to_id(self, obj):
        if isinstance(obj, leancloud.Object):
            if obj.id is None:
                raise TypeError('cant add an unsaved Object to a relation')
            if self._target_class_name is None:
                self._target_class_name = obj._class_name
            if self._target_class_name != obj._class_name:
                raise TypeError('try to create a Relation with 2 different types')
            return obj.id
        return obj

    @property
    def added(self):
        objs = []
        for obj_id in self.relations_to_add:
            obj = leancloud.Object.create(self._target_class_name)
            obj.id = obj_id
            objs.append(obj)
        return objs

    @property
    def removed(self):
        objs = []
        for obj_id in self.relations_to_remove:
            obj = leancloud.Object.create(self._target_class_name)
            obj.id = obj_id
            objs.append(obj)
        return objs

    def dump(self):
        adds = None
        removes = None

        def id_to_pointer(id_):
            return {
                '__type': 'Pointer',
                'className': self._target_class_name,
                'objectId': id_,
            }
        if len(self.relations_to_add) > 0:
            adds = {
                '__op': 'AddRelation',
                'objects': [id_to_pointer(x) for x in self.relations_to_add]
            }
        if len(self.relations_to_remove) > 0:
            removes = {
                '__op': 'RemoveRelation',
                'objects': [id_to_pointer(x) for x in self.relations_to_remove]
            }

        if adds and removes:
            return {
                '__op': 'Batch',
                'ops': [adds, removes]
            }

        return adds or removes or {}

    def _merge(self, previous=None):
        if previous is None:
            return self
        elif isinstance(previous, Unset):
            raise ValueError('can\'t modify a relation after deleting it.')
        elif isinstance(previous, Relation):
            if (previous._target_class_name) and (previous._target_class_name != self._target_class_name):
                raise TypeError('related object must be class of {0}'.format(previous._target_class_name))
            new_add = (previous.relations_to_add - self.relations_to_remove) | self.relations_to_add
            new_remove = (previous.relations_to_remove - self.relations_to_add) | self.relations_to_remove

            new_relation = Relation(new_add, new_remove)
            new_relation._target_class_name = self._target_class_name
            return new_relation
        else:
            raise TypeError('invalid op')

    def _apply(self, old, obj=None, key=None):
        if old is None:
            return leancloud.Relation(obj, key)
        elif isinstance(old, leancloud.Relation):
            if self._target_class_name:
                if old.target_class_name:
                    if old.target_class_name != self._target_class_name:
                        raise TypeError('related object must be class of {0}'.format(old.target_class_name))
                    else:
                        old.target_class_name = self._target_class_name
                return old
            else:
                raise TypeError('invalid op')
