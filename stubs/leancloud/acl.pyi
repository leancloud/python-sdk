from typing import Union, Dict

import leancloud
from leancloud.user import User 
from leancloud.role import Role


user_type = Union[str, User, Role]
role_type = Union[Role, str]

class ACL(object):
    permissions_by_id = ... #type: Dict
    def __init__(self, permissions_by_id: Dict=None) -> None: ...

    def dump(self) -> Dict:...

    def _set_access(self, access_type: str, user_id: user_type, allowed: bool) -> None:...

    def _get_access(self, access_type: str, user_id: user_type) -> bool:...

    def set_read_access(self, user_id: user_type, allowed: bool) -> None:...

    def get_read_access(self, user_id: user_type) -> None:...

    def set_write_access(self, user_id: user_type, allowed: bool) -> None:...

    def get_write_access(self, user_id: user_type) -> bool:...

    def set_public_read_access(self, allowed: bool) -> None:...

    def get_public_read_access(self) -> bool:...

    def set_public_write_access(self, allowed: bool) -> None:...

    def get_public_write_access(self) -> bool:...

    def set_role_read_access(self, role: role_type, allowed: bool) -> None:...

    def get_role_read_access(self, role: role_type) -> bool:...

    def set_role_write_access(self, role: role_type, allowed: bool) -> None:...

    def get_role_write_access(self, role: role_type) -> bool:...
