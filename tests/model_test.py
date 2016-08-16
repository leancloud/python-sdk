import os
import datetime
import random

from nose.tools import with_setup
from nose.tools import eq_
from nose.tools import raises 

import leancloud
from leancloud.models import models
from leancloud.models.models import ModelMeta
from leancloud.models.fields import *
from leancloud import relation
from leancloud.errors import LeanCloudError

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
    class Person(models.UserModel):
        hobby = StringField()

    plato = Person(
        username = 'Plato', 
        password = 'philosophy',
        hobby = 'plaza talk'
    )
    return plato

def test_user_sign_up():
    plato = get_person()
    plato.sign_up()
    assert plato.id

def test_destroy():
    republic = get_book()
    republic.save()
    id = republic.id
    leancloud.Query('Book').get(id)
    republic.destroy()

def get_book():
    class Book(models.Model):
        readers_num = NumberField()
        influnced = ArrayField()
        published_at = DateField()
        title = StringField()
        is_Greek = BooleanField()
        index = FileField()
        related_book = PointerField()
        auther = UserField()
        readers = RelationField()

    import cStringIO
    s1 = cStringIO.StringIO()
    s1.write('whatever')

    logos = Book(title='logos')

    republic =  Book(
        readers_num=1,
        influnced=[],
        # published_at=datetime.datetime.now(),
        title='Repulic',
        is_Greek=True,
        index = leancloud.file_.File('chapter', s1),
        related_book=logos,
        auther=get_person(),
    )
    return republic

def test_set_relation():
    republic = get_book()
    republic.save()
    plato = get_person()
    plato.save()
    readers = republic.relation('readers')
    readers.add(plato)
    republic.save()

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
    class Book(models.Model):
        author = StringField()
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

@raises(ValueError)
def test_verifier():
    def verify(value):
        if value <= 10:
            raise ValueError('value too small')

    class Book(models.Model):
        pages = NumberField(verifier=verify)

    republic = Book()
    republic.pages = 9

@with_setup(setup)
def test_initial_save():
    republic = get_book()
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

def test_reset_password_by_sms_code():
    plato = get_person()
    try:
        plato.reset_password_by_sms_code('1861111' + str(random.randrange(1000, 9999)), "password")
    except LeanCloudError as e:
        if e.code != 1:
            raise e

def test_get_bases():
    class A(object): pass
    class B(A): pass
    class C(B): pass
    class D(C, B): pass

    assert ModelMeta._get_all_bases(()) == ()
    assert ModelMeta._get_all_bases((object,)) == ()
    assert ModelMeta._get_all_bases((A,)) == (A,)
    assert ModelMeta._get_all_bases((B,)) == (B, A)
    assert ModelMeta._get_all_bases((C,)) == (C, B, A)
    assert ModelMeta._get_all_bases((D,)) == (D, C, B, A)

