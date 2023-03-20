# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import warnings

import requests

import leancloud

warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()


os.environ["APP_ID"] = os.environ.get(
    "APP_ID", "vpLjcQSLouokjRBMFIS8yiti-9Nh9j0Va"
)
os.environ["APP_KEY"] = os.environ.get(
    "APP_KEY", "yIME5gwf7vk6ZKF0BWUliVgJ"
)
os.environ["MASTER_KEY"] = os.environ.get(
    "MASTER_KEY", "ycfIrMY2j8W7p8DGARBCRIfe"
)
os.environ["HOOK_KEY"] = os.environ.get("HOOK_KEY", "YWR0Gy0MQRf2s4vIaFTT9pPp")
leancloud.use_region(os.environ.get("USE_REGION", "CN"))
