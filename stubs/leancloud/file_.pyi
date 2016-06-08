import leancloud
from leancloud.object_ import Object
from leancloud.acl import ACL

import sys
from typing import Union, Dict, SupportsFloat, Any


class File(Object):

    # data type of file or StringIO
    def __init__(self, name: str, data: Any=None, type_: str=None) -> None:...

    @classmethod
    def create_with_url(cls, name: str, url: str, meta_data: Dict =None, type_: str=None):...

    @classmethod
    def create_without_data(cls, object_id: str):...

    def get_acl(self):...

    def set_acl(self, acl: ACL):...

    def name(self):...

    def url(self):...

    def size(self):...

    def owner_id(self):...

    def metadata(self):...

    def get_thumbnail_url(self, width: SupportsFloat, height: SupportsFloat, quality: SupportsFloat, scale_to_fit: bool=True, fmt: str='png'):...

    def destroy(self):...

    def _save_to_qiniu(self):...

    def _save_to_leancloud(self):...

    def save(self):...

    def _save_external(self):...

    def _save_to_cos(self):...

    def fetch(self):...
