#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
from vulcanus.manage import init_application
from vulcanus.restful.serialize import validate
from vulcanus.send_email import Email
from vulcanus.token import decode_token, generate_token
from vulcanus.log.log import LOGGER
from vulcanus.conf import configuration as setting
from vulcanus.database.proxy import connect_database
from vulcanus.timed import TimedTask, TimedTaskManager


__all__ = (
    "init_application",
    "validate",
    "Email",
    "decode_token",
    "generate_token",
    "LOGGER",
    "setting",
    "connect_database",
    "TimedTask",
    "TimedTaskManager",
)
