# coding: utf-8

import leancloud

__author__ = 'asaka'


class BaseOperation(object):
    pass


class Set(BaseOperation):
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self.value

    def dump(self):
        return _encode(self.value)


class Unset(BaseOperation):
    def __init__(self):
        pass

    def dump(self):
        return {
            '__op': 'Delete'
        }


class Increment(BaseOperation):
    def __init__(self, amount):
        self.amount = amount

    @property
    def amount(self):
        return self.amount

    def dump(self):
        return {
            '__op': 'Increment',
            'amount': self.amount,
        }


class Add(BaseOperation):
    def __init__(self, objects):
        self.objects = objects

    @property
    def objects(self):
        return self.objects

    def dump(self):
        return {
            '__op': 'Add',
            'objects': _encode(self.objects),
        }


class AddUnique(BaseOperation):
    def __init__(self, objects):
        self.objects = list(set(objects))

    @property
    def objects(self):
        return self.objects

    def dump(self):
        return {
            '__op': 'AddUnique',
            'objects': _encode(self.objects),
        }


class Remove(BaseOperation):
    def __init__(self, objects):
        self.objects = list(set(objects))

    @property
    def objects(self):
        return self.objects

    def dump(self):
        return {
            '__op': 'Remove',
            'objects': _encode(self.objects)
        }


class Relation(BaseOperation):
    def __init__(self, adds, removes):
        self._target_class_name = None

        self.relations_to_add = list({self._pointer_to_id(x) for x in adds})
        self.relations_to_removes = list({self._pointer_to_id(x) for x in removes})

    def _pointer_to_id(self, obj):
        if isinstance(obj, leancloud.Object):
            if not hasattr(obj, 'id'):   # TODO: how to decide an object is unsaved ?
                raise TypeError('cant add an unsaved Object to a relation')
            if self._target_class_name is None:
                self._target_class_name = obj.class_name
            if self._target_class_name != obj.class_name:
                raise TypeError('try to create a Relation with 2 different types')
            return obj.id
        return obj

    @property
    def added(self):
        # TODO
        pass

    @property
    def removed(self):
        # TODO
        pass

    def dump(self):
        adds = None
        removes = None
        id_to_pointer = lambda id_: {
            '__type': 'Pointer',
            'class_name': self._target_class_name,
            'object_id': id_,
        }
        if len(self.relations_to_add) > 0:
            adds = {
                '__op': 'AddRelation',
                'objects': [id_to_pointer(x) for x in self.relations_to_add]
            }
        if len(self.relations_to_removes) > 0:
            removes = {
                '__op': 'RemoveRelation',
                'objects': [id_to_pointer(x) for x in self.relations_to_removes]
            }

        if (adds and removes):
            return {
                '__op': 'Batch',
                'ops': [adds, removes]
            }

        return adds or removes or {}
