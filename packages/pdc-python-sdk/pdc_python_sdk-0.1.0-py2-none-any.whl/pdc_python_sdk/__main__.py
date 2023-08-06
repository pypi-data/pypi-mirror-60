# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2020 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
本文件允许模块包以python -m pdc_python_sdk方式直接执行。

Authors: jiaqianjing(jiaqianjing@baidu.com)
Date:    2020/02/04 16:06:56
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


import sys
from pdc_python_sdk.cmdline import main
sys.exit(main())
