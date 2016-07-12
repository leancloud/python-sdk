import os
import datetime

from nose.tools import with_setup
from nose.tools import eq_
from nose.tools import raises 

import leancloud
from leancloud.models import model
from leancloud.models import field


def setup():
    leancloud.client.USE_MASTER_KEY = None
    leancloud.client.APP_ID = None
    leancloud.client.APP_KEY = None
    leancloud.client.MASTER_KEY = None
    leancloud.init(
    os.environ['APP_ID'],
    os.environ['APP_KEY']
    )

def get_person():
    class Person(model.UserModel):
        hobby = field.String()

    plato = Person(
        username = 'Plato', 
        password = 'philosophy',
        hobby = 'plaza talk'
    )
    return plato


def get_book():
    class Book(model.Model):
        readers_num = field.Number()
        influnced = field.Array()
        published_at = field.Date()
        title = field.String()
        is_Greek = field.Boolean()
        index = field.File()
        related_book = field.Pointer()
        auther = field.User()
        readers = field.Relation()

    import cStringIO
    s1 = cStringIO.StringIO()
    s1.write('whatever')

    logos = Book(title='Logos')

    republic =  Book(
      #  readers_num=1, 
      #  influnced=[], 
      #  published_at=datetime.datetime.now(), 
      #  title='Repulic', 
      #  is_Greek=True, 
      #  index = leancloud.file_.File('chapter', s1),
        related_book=logos
      #  auther=None, 
      #  readers=None
    )
    return republic

def test_set_field_value():
    republic = get_book()
    republic.readers_num = 3
    eq_(republic.readers_num, 3)

@raises(AttributeError)
def test_del_field():
    republic = get_book()
    del republic.readers_num
    republic.readers_num

@raises(AttributeError)
def test_set_with_incrrect_field_name():
    class Book(model.Model):
        author = field.String()
    Book(reader='Plato')

def test_increment():
    republic = get_book()
    republic.increment('readers_num', 1)
    republic.readers_num
    eq_(republic.readers_num, 2)

@raises(ValueError)
def test_validate_num():
    republic = get_book()
    republic.readers_num = 'a'

@with_setup(setup)
def test_initial_save():
    republic = get_book()
    print(republic._object._attributes)
    republic.save()
    assert republic.id
    assert republic.created_at

@with_setup(setup)
def test_update_save():
    republic = get_book()
    republic.save()
    republic.increment('readers_num', 2)
    republic.save()
    assert republic.updated_at - republic.created_at

# test plan. all fields, 

