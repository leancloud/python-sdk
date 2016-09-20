# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import warnings

import leancloud

warnings.warn('leancloud.engine.cloudfunc should not be used any more, please use leancloud.cloudfunc instead', leancloud.errors.LeanCloudWarning)

run = leancloud.cloudfunc.run
rpc = leancloud.cloudfunc.rpc
request_sms_code = leancloud.cloudfunc.request_sms_code
verify_sms_code = leancloud.cloudfunc.verify_sms_code
