# coding: utf-8

import requests
import os
import leancloud

requests.packages.urllib3.disable_warnings()


try:
    os.environ['APP_ID']
except KeyError:
    os.environ['APP_ID'] = 'pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb'
else:
    import leancloud.client
    leancloud.client.TIMEOUT_SECONDS = 60


try:
    os.environ['APP_KEY']
except KeyError:
    os.environ['APP_KEY'] = 'hi4jsm62kok2qz2w2qphzryo564rzsrucl2czb0hn6ogwwnd'


try:
    os.environ['MASTER_KEY']
except KeyError:
    os.environ['MASTER_KEY'] = 'azkuvukzlq3t38abdrgrwqqdcx9me6178ctulhd14wynfq1n'


try:
    leancloud.client.IMEOUT_SECONDS = int(os.environ['TRAVIS_TIMEOUT'])
except KeyError:
    pass
