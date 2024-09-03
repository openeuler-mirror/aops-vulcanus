#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2024. All rights reserved.
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
GLOBAL_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'aops-config.yml')
DEFAULT_CUSTOM_CONF_DIR_PATH = os.path.join(BASE_CONFIG_PATH, 'conf.d')

# canal config
CANAL_BIN_PATH = "/usr/share/canal/bin/"
CANAL_ADAPTER_BIN_PATH = "/usr/share/canal-adapter/bin/"
CANAL_CONF_PATH = "/usr/share/canal/conf/"
CANAL_ADAPTER_CONF_PATH = "/usr/share/canal-adapter/conf/"
CANAL_ADAPTER_APPLICATION = "/usr/share/canal-adapter/conf/application.yml"
CANAL_PROPERTIES = "/usr/share/canal/conf/canal.properties"
INSTANCE_PATH = "/etc/aops/sync-conf.d/instance.properties"
CANAL_INSTANCE = "/instance.properties"
RDB_CONF_PATH = "/etc/aops/sync-conf.d/rdb/"
CANAL_DB_USERNAME = "canal"
CANAL_DB_PASSWORD = "canal"

# url format
URL_FORMAT = "http://%s:%s%s"

PRIVATE_INDIVIDUATION_CONFIG = os.path.join(BASE_CONFIG_PATH, ".aops-private-config.ini")

# The root node of the zookeeper configuration center
CONFIG_ROOT_PATH = "/config"
SERVICE_CUSTOM_CONFIG_PATH = os.path.join(CONFIG_ROOT_PATH, "/services")
REFRESH_TOKEN_EXP = 1440
TIMEOUT = 900

# default password
DEFAULT_PASSWORD = "changeme"


class TaskStatus:
    SUCCEED = "succeed"
    FAIL = "fail"
    RUNNING = "running"
    UNKNOWN = "unknown"


class UserRoleType:
    ADMINISTRATOR = "administrator"
    NORMAL = "normal"


ADMIN_USER = "admin"

# hosts service api
HOSTS = "/hosts"
HOSTS_FILTER = "/hosts/filter"
BATCH_ADD_HOSTS = "/hosts/batch"
HOSTS_STATUS = "/hosts/status"
HOSTS_COUNT = "/hosts/count"
HOSTS_TEMPLATE = "/hosts/template/file"
HOSTS_GROUP = "/hosts/group"
ALL_HOST_GROUP_MAP = "/hosts/group/all-host"
HOSTS_IP_FILTER = "/hosts/ips"

# user service api
USER_LOGIN = "/accounts/login"
CHANGE_PASSWORD = "/accounts/password"
ADD_USER = "/accounts/register"
GITEE_AUTH_LOGIN = "/accounts/gitee/login"
AUTH_REDIRECT_URL = "/accounts/auth/redirecturl"
BIND_AUTH_ACCOUNT = "/accounts/auth/bind"
REFRESH_TOKEN = "/accounts/refreshtoken"
LOGOUT = "/accounts/logout"
LOGOUT_REDIRECT = "/accounts/logout/redirect"
PERMISSION_BIND = "/accounts/permission/bind"
PERMISSIONS = "/accounts/permission"
USERS = "/accounts"
USERS_ALL = "/accounts/all"
CLUSTER_SYNC = "/accounts/cluster/sync"
ACCESS_TOKEN = "/accounts/accesstoken"
OAUTH2_AUTHORIZE_URI = "/accounts/authorize-uri"

# oauth2 api
OAUTH2_AUTHORIZE_TOKEN = "/oauth2/token"
OAUTH2_LOGIN = "/oauth2/login"
OAUTH2_LOGOUT = "/oauth2/logout"
OAUTH2_REFRESH_TOKEN = "/oauth2/refresh-token"
OAUTH2_INTROSPECT = "/oauth2/introspect"
OAUTH2_AUTHORIZE = "/oauth2/authorize"
OAUTH2_REVOKE_TOKEN = "/oauth2/revoke-token"
OAUTH2_APPLICATIONS = "/oauth2/applications"
OAUTH2_APPLICATIONS_REGISTER = "/oauth2/applications/register"
OAUTH2_APPLICATIONS_INFO = "/oauth2/applications/"
OAUTH2_MANAGE_LOGIN = "/oauth2/manager-login"
OAUTH2_PASSWORD_CHENAGE = "/oauth2/password"
OAUTH2_REGISTER_USER = "/oauth2/register"


# auth login
GITEE_OAUTH = "https://gitee.com/oauth/authorize"
GITEE_TOKEN = "https://gitee.com/oauth/token?grant_type=authorization_code"
GITEE_USERINFO = "https://gitee.com/api/v5/user"

# zeus cluster manager
REGISTER_CLUSTER = "/accounts/cluster/register"
REGISTER_CLUSTER_BATCH = "/accounts/cluster/register/batch"
MANAGED_CLUSTER = "/accounts/cluster"
CLUSTER_PERMISSION_CACHE = "/accounts/permission/cache"
CLUSTER_USER_BIND = "/accounts/cluster/bind"
CLUSTER_MANAGED_CANCEL = "/accounts/cluster/cancle"
CLUSTER_PRIVATE_KEY = "/accounts/cluster/key"

CLUSTER_MANAGE = "/hosts/cluster"
LOCAL_CLUSTER_INFO = "/hosts/subcluster"
CLUSTER_GROUP_CACHE = "/hosts/cluster/group/cache"

# distribute
DISTRIBUTE = "/distribute"

# ceres support command
CERES_PLUGIN_START = "aops-ceres plugin --start '%s'"
CERES_PLUGIN_STOP = "aops-ceres plugin --stop '%s'"
CERES_COLLECT_ITEMS_CHANGE = "aops-ceres plugin --change-collect-items '%s'"
CERES_PLUGIN_INFO = "aops-ceres plugin --info"
CERES_APPLICATION_INFO = "aops-ceres collect --application"
CERES_COLLECT_FILE = "aops-ceres collect --file '%s'"
CERES_HOST_INFO = "aops-ceres collect --host '%s'"
CERES_CVE_REPO_SET = "aops-ceres apollo --set-repo '%s'"
CERES_CVE_SCAN = "aops-ceres apollo --scan '%s'"
CERES_CVE_FIX = "aops-ceres apollo --fix '%s'"
CERES_CVE_ROLLBACK = "aops-ceres apollo --rollback '%s'"
CERES_HOTPATCH_REMOVE = "aops-ceres apollo --remove-hotpatch '%s'"
CERES_SYNC_CONF = "aops-ceres ragdoll --sync '%s'"
CERES_OBJECT_FILE_CONF = "aops-ceres ragdoll --list '%s'"

# ragdoll conf trace manager
CREATE_DOMAIN = "/conftrace/domain/createDomain"
DELETE_DOMAIN = "/conftrace/domain/deleteDomain"
QUERY_DOMAIN = "/conftrace/domain/queryDomain"
ADD_HOST_IN_DOMAIN = "/conftrace/host/addHost"
DELETE_HOST_IN_DOMAIN = "/conftrace/host/deleteHost"
GET_HOST_BY_DOMAIN = "/conftrace/host/getHost"
GET_NOT_EXIST_HOST = "/conftrace/host/getNonexistentHost"
ADD_MANAGEMENT_CONFS_IN_DOMAIN = "/conftrace/management/addManagementConf"
UPLOAD_MANAGEMENT_CONFS_IN_DOMAIN = "/conftrace/management/uploadManagementConf"
DELETE_MANAGEMENT_CONFS_IN_DOMAIN = "/conftrace/management/deleteManagementConf"
GET_MANAGEMENT_CONFS_IN_DOMAIN = "/conftrace/management/getManagementConf"
QUERY_CHANGELOG_OF_MANAGEMENT_CONFS_IN_DOMAIN = "/conftrace/management/queryManageConfChange"
GET_SYNC_STATUS = "/conftrace/confs/getDomainStatus"
QUERY_EXCEPTED_CONFS = "/conftrace/confs/queryExpectedConfs"
QUERY_REAL_CONFS = "/conftrace/confs/queryRealConfs"
SYNC_CONF_TO_HOST_FROM_DOMAIN = "/conftrace/confs/syncConf"
QUERY_SUPPORTED_CONFS = "/conftrace/confs/querySupportedConfs"
COMPARE_CONF_DIFF = "/conftrace/confs/domain/diff"
BATCH_SYNC_CONF_TO_HOST_FROM_DOMAIN = "/conftrace/confs/batch/syncConf"
HOST_CONF_SYNC_STATUS = "/conftrace/host/sync/status/get"
HOST_DELETE_TASK = "host_delete_task"
