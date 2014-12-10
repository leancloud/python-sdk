# coding: utf-8

import copy

import leancloud
import leancloud.utils

__author__ = 'asaka'


class BaseOp(object):
    def dump(self):
        raise NotImplementedError

    def _merge_with_previous(self, previous):
        raise NotImplementedError

    def _estimate(self, old):
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

    def _merge_with_previous(self, previous):
        return self

    def _estimate(self, old):
        return self.value


class Unset(BaseOp):
    def __init__(self):
        pass

    def dump(self):
        return {
            '__op': 'Delete'
        }

    def _merge_with_previous(self, previous):
        return self

    def _estimate(self, old):
        return _UNSET


class Increment(BaseOp):
    def __init__(self, amount):
        self._amount = amount

    @property
    def amount(self):
        return self._amount

    def dump(self):
        return {
            '__op': 'Increment',
            'amount': self.amount,
        }

    def _merge_with_previous(self, previous):
        if not previous:
            return self
        elif isinstance(previous, Unset):
            return Set(self.amount)
        elif isinstance(previous, Set):
            return Set(previous.value, self.amount)
        elif isinstance(previous, Increment):
            return Increment(self.amount + previous.amount)
        else:
            raise TypeError('invalid op')

    def _estimate(self, old):
        if not old:
            return self.amount
        return old + self.amount


class Add(BaseOp):
    def __init__(self, objects):
        self._objects = objects

    @property
    def objects(self):
        return self._objects

    def dump(self):
        return {
            '__op': 'Add',
            'objects': leancloud.utils.encode(self.objects),
        }

    def _merge_with_previous(self, previous):
        if not previous:
            return self
        elif isinstance(previous, Unset):
            return Set(self.objects)
        elif isinstance(previous, Set):
            return Set(self._estimate(previous.value))
        elif isinstance(previous, Add):
            return Add(previous.objects + self.objects)
        else:
            raise TypeError('invalid op')

    def _estimate(self, old):
        if not old:
            return copy.deepcopy(self.objects)
        else:
            return old + self.objects


class AddUnique(BaseOp):
    def __init__(self, objects):
        self._objects = list(set(objects))

    @property
    def objects(self):
        return self._objects

    def dump(self):
        return {
            '__op': 'AddUnique',
            'objects': leancloud.utils.encode(self.objects),
        }

    def _merge_with_previous(self, previous):
        if not previous:
            return self
        elif isinstance(previous, Unset):
            return Set(self.objects)
        elif isinstance(previous, Set):
            return Set(self._estimate(previous.value))
        elif isinstance(previous, AddUnique):
            return AddUnique(self._estimate(previous.objects))
        else:
            raise TypeError('invalid op')

    def _estimate(self, old):
        if not old:
            return copy.deepcopy(self.objects)
        new = copy.deepcopy(old)
        # TODO
        raise NotImplementedError


class Remove(BaseOp):
    def __init__(self, objects):
        self._objects = list(set(objects))

    @property
    def objects(self):
        return self._objects

    def dump(self):
        return {
            '__op': 'Remove',
            'objects': leancloud.utils.encode(self.objects)
        }

    def _merge_with_previous(self, previous):
        # TODO
        raise NotImplementedError

    def _estimate(self, old):
        # TODO
        raise NotImplementedError


class Relation(BaseOp):
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

        if adds and removes:
            return {
                '__op': 'Batch',
                'ops': [adds, removes]
            }

        return adds or removes or {}

    def _merge_with_previous(self, previous):
        # TODO
        raise NotImplementedError

    def _estimate(self, old):
        # TODO
        raise NotImplementedError