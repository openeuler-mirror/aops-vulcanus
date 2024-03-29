#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Time:
Author:
Description: config constant
"""
import os

BASE_CONFIG_PATH = "/etc/aops"

# path of global configuration
SYSTEM_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'system.ini')

# url format
URL_FORMAT = "http://%s:%s%s"

PRIVATE_INDIVIDUATION_CONFIG = os.path.join(BASE_CONFIG_PATH, ".aops-private-config.ini")


REFRESH_TOKEN_EXP = 1440
TIMEOUT = 900
