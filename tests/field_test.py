import leancloud 
from leancloud.models.fields import *

def test_string_field_validation():
    chapter = StringField(max_len=1)
    chapter.validate('abc')
    
