import os
import sys

from nose.tools import with_setup
from nose.tools import eq_
from nose.tools import raises 

import leancloud

from .. import model
from .. import field

def setup():
    leancloud.client.USE_MASTER_KEY = None
    leancloud.client.APP_ID = None
    leancloud.client.APP_KEY = None
    leancloud.client.MASTER_KEY = None
    leancloud.init(
    os.environ['APP_ID'],
    os.environ['APP_KEY']
    )

def get_book():
    class Book(model.Model):
        readers_num = field.Number()
    return Book(readers_num=1)

def test_set_field_value():
    apology = get_book()
    apology.readers_num = 3
    eq_(apology.readers_num, 3)
    #assert apology.fields['readers_num'].current

@raises(AttributeError)
def test_del_field():
    apology = get_book()
    del apology.readers_num
    apology.readers_num

def test_increment():
    apology = get_book()
    apology.increment('readers_num', 1)
    apology.readers_num
    #print(apology._object.attributes)
    #eq_(apology.readers_num, 2)

@raises(ValueError)
def test_validate_num():
    apology = get_book()
    apology.readers_num = 'a'

@with_setup(setup)
def test_initial_save():
    apology = get_book()
    apology.save()
    assert apology.id
    assert apology.created_at

@with_setup(setup)
def test_update_save():
    apology = get_book()
    apology.save()
    apology.increment('readers_num', 2)
    apology.save()
    assert apology.updated_at - apology.created_at
