from typing import Union, Tuple, Dict
from datetime import datetime

import leancloud
from leancloud.query import Query


def send(data: Dict, channels: Union[List,Tuple]=None, push_time: datetime=None, expiration_time: datetime=None, expiration_interval: int=None, where: Query=None, cql: str=None):...
