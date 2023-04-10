#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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

BASE_CONFIG_PATH = '/etc/aops'

# path of global configuration
SYSTEM_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'system.ini')

# path of proxy configuration
MANAGER_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'manager.ini')


TASK_INDEX = "ansible_task"

# url format
URL_FORMAT = "http://%s:%s%s"

# manager route
ADD_HOST = "/manage/host/add"
ADD_HOST_BATCH = "/manage/host/add/batch"
GET_HOST_TEMPLATE_FILE = "/manage/host/file/template"
DELETE_HOST = "/manage/host/delete"
QUERY_HOST = "/manage/host/get"
GET_HOST_COUNT = "/manage/host/count"
AUTH_REDIRECT_URL = "/manage/account/authredirecturl"
BIND_AUTH_ACCOUNT = "/manage/account/bindaccount"
REFRESH_TOKEN = "/manage/account/refreshtoken"
UPDATE_HOST = "/manage/host/update"

QUERY_HOST_DETAIL = "/manage/host/info/query"
HOST_SCENE_GET = '/manage/host/scene/get'

ADD_GROUP = "/manage/host/group/add"
DELETE_GROUP = "/manage/host/group/delete"
GET_GROUP = "/manage/host/group/get"

COLLECT_CONFIG = '/manage/config/collect'

USER_LOGIN = "/manage/account/login"
CHANGE_PASSWORD = '/manage/account/change'
ADD_USER = '/manage/account/add'
GITEE_AUTH_LOGIN = "/manage/account/gitee/login"

AGENT_PLUGIN_INFO = '/manage/agent/plugin/info'
AGENT_PLUGIN_SET = '/manage/agent/plugin/set'
AGENT_METRIC_SET = '/manage/agent/metric/set'

EXECUTE_REPO_SET = '/manage/vulnerability/repo/set'
EXECUTE_CVE_FIX = '/manage/vulnerability/cve/fix'
EXECUTE_CVE_SCAN = '/manage/vulnerability/cve/scan'

# metric config
QUERY_METRIC_NAMES = '/manage/host/metric/names'
QUERY_METRIC_DATA = '/manage/host/metric/data'
QUERY_METRIC_LIST = '/manage/host/metric/list'

# auth login
GITEE_OAUTH = "https://gitee.com/oauth/authorize"
GITEE_CLIENT_ID = "7420ebbb10f7f196de479bd3fe30f120691321143fdae882bc8b3320b3dbb71c"
GITEE_TOKEN = "https://gitee.com/oauth/token?grant_type=authorization_code"
GITEE_CLIENT_SECRET = "c6466348389db3a2da3a86ec3b544c19c15f50de513da4dc3edbadaa2e5df792"
GITEE_USERINFO = "https://gitee.com/api/v5/user"
PRIVATE_KEY = "sfwsfs{)sdf_+$%{$^%$NI07&*()@$&^*(*(^&%("

# Refresh the token validity period，unit minute
REFRESH_TOKEN_EXP = 1440
REDIRECT_URL = "http://127.0.0.1:8000/user/account"
