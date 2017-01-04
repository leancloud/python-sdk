import leancloud 
from leancloud.models.fields import *

def test_string_field_validation():
    chapter = StringField(regex='^b')
    chapter.validate('abc')

    
