# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import requests
import os
import leancloud

requests.packages.urllib3.disable_warnings()


os.environ['APP_ID'] = os.environ.get('APP_ID', 'pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb')
os.environ['APP_KEY'] = os.environ.get('APP_KEY', 'hi4jsm62kok2qz2w2qphzryo564rzsrucl2czb0hn6ogwwnd')
os.environ['MASTER_KEY'] = os.environ.get('MASTER_KEY', 'azkuvukzlq3t38abdrgrwqqdcx9me6178ctulhd14wynfq1n')
leancloud.use_region(os.environ.get('USE_REGION', 'CN'))
