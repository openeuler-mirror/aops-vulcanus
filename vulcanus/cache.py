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
import json
from typing import Optional

from flask import g
from redis.client import Redis
from redis.exceptions import RedisError
from vulcanus.conf.constant import (
    ALL_HOST_GROUP_MAP,
    CLUSTER_GROUP_CACHE,
    CLUSTER_MANAGE,
    CLUSTER_PERMISSION_CACHE,
    CLUSTER_PRIVATE_KEY,
    LOCAL_CLUSTER_INFO,
)
from vulcanus.database.proxy import RedisProxy
from vulcanus.log.log import LOGGER
from vulcanus.restful.resp import state
from vulcanus.restful.response import BaseResponse


class RedisCacheManage:
    """Class for managing Redis cache."""

    # Redis Keys Constant
    ALL_CLUSTER_KEY = "clusters"  # hashmap e.g {"cluster_id": {"cluster_id": "cluster_id", "cluster_ip": "cluster_ip"}}
    CLUSTER_GROUPS = "cluster_groups"  # hashmap e.g.{"cluster_id": [{"group_id": "group_name"},],}
    USER_CLUSTER_SUFFIX = "_clusters"  # hashmap e.g {"cluster_id": 'cluster_name'}
    USER_GROUPS_SUFFIX = "_group_hosts"  # hashmap e.g {"group_id": "group_name"}
    USER_ROLES_SUFFIX = "_role"
    USER_CLUSTER_PRIVATE_KEY_SUFFIX = "_rsa_key"
    SCANNING_HOST_KEY = "scanning_host_set"  # hashmap e.g {"host_id": "Timestamp of scan time", "host_id": 1716167968}
    LOCATION_CLUSTER = "location_cluster"  # hashmap e.g {"cluster_id": 'xxx',"cluster_name": "mock_name"}
    GROUPS_HOSTS = "groups_hosts"  # hashmap e.g {"group_id": ["host_id", "host_id"]}

    def __init__(self, domain: str, redis_client: Redis = None, username=None) -> None:
        """
        Initializes RedisCacheManage object.

        Args:
            redis_client (Redis): Redis client object.
            domain (str): Domain information.
        """
        self.client = redis_client or RedisProxy.redis_connect
        self.domain = f"http://{domain}"
        self._username = username

    def _remote_api(self, url, method="GET", data=None, headers=None):
        """
        Perform a remote API call.

        Args:
            url (str): API URL.
            method (str): HTTP method.
            data (dict): Request data.

        Returns:
            BaseResponse: API response.
        """
        if headers is None:
            headers = self.headers
        response = BaseResponse.get_response(url=url, method=method, data=data, header=headers)
        if response["label"] != state.SUCCEED:
            return False, None

        return True, response.get("data")

    @property
    def username(self):
        return self._username or g.username

    @property
    def headers(self):
        return g.headers

    @property
    def user_clusters_key(self) -> str:
        return self.username + RedisCacheManage.USER_CLUSTER_SUFFIX

    @property
    def user_groups_key(self) -> str:
        return self.username + RedisCacheManage.USER_GROUPS_SUFFIX

    @property
    def user_roles_key(self) -> str:
        return self.username + RedisCacheManage.USER_ROLES_SUFFIX

    @property
    def user_private_key(self) -> str:
        return self.username + RedisCacheManage.USER_CLUSTER_PRIVATE_KEY_SUFFIX

    def hash(self, key: str) -> Optional[dict]:
        """
        Queries hash type data from Redis.

        Args:
            key (str): Redis key.

        Returns:
            Optional[dict]: query result.
        """
        try:
            if self.client.exists(key):
                return self.client.hgetall(key)
        except RedisError as error:
            LOGGER.error(error)

        return None

    def string(self, key: str) -> Optional[str]:
        """
        Queries string type data from Redis.

        Args:
            redis_key (str): Redis key.

        Returns:
            Optional[str]: query result.
        """
        try:
            if self.client.exists(key):
                return self.client.get(key)
        except RedisError as error:
            LOGGER.error(error)

        return None

    def list(self, key: str) -> Optional[list]:
        """
        Queries list type data from Redis.

        Args:
            key (str): Redis key.

        Returns:
            Optional[list]: query result.
        """
        try:
            if self.client.exists(key):
                return [item for item in self.client.lrange(key, 0, -1)]

        except RedisError as error:
            LOGGER.error(error)
        return None

    def set(self, key: str) -> Optional[set]:
        """
        Queries set type data from Redis.

        Args:
            key (str): Redis key

        Returns:
            Optional[set]: query result.
        """
        try:
            if self.client.exists(key):
                return {item for item in self.client.smembers(key)}

        except RedisError as error:
            LOGGER.error(error)
        return None

    def _json_decode(self, data: str) -> Optional[dict]:
        """
        Decodes JSON data.

        Args:
            data (str): JSON data.

        Returns:
            Optional[dict]: decoded data.
        """
        try:
            return json.loads(data)
        except json.JSONDecodeError as error:
            LOGGER.debug(error)
        return data

    def get_user_clusters(self) -> Optional[dict]:
        """
        Retrieves user clusters information from Redis.

        Returns:
            Optional[dict]: query result.
        """
        data = self.hash(self.user_clusters_key)
        if data is not None:
            return data

        _, _ = self._remote_api(url=self.domain + CLUSTER_PERMISSION_CACHE)
        return self.hash(self.user_clusters_key) or dict()

    def get_user_group_hosts(self) -> Optional[dict]:
        """
        Retrieves user groups information from Redis.

        Returns:
            tuple: A tuple containing the status code and the query result.
        """
        data = self.hash(self.user_groups_key)
        if data is not None:
            return data

        _, _ = self._remote_api(url=self.domain + CLUSTER_PERMISSION_CACHE)
        return self.hash(self.user_groups_key) or dict()

    @property
    def clusters(self) -> Optional[dict]:
        """
        Retrieves clusters information from Redis.

        Returns:
            Optional[dict]: query result.
        """
        data = self.hash(self.ALL_CLUSTER_KEY)
        if data is not None:
            return {key: self._json_decode(value) for key, value in data.items()}

        response, _ = self._remote_api(url=self.domain + CLUSTER_MANAGE)
        if response:
            cache_data = self.hash(self.ALL_CLUSTER_KEY) or dict()
            return {key: self._json_decode(value) for key, value in cache_data.items()}

        return dict()

    @property
    def user_role(self):
        role = self.string(self.user_roles_key)
        if role is not None:
            return role
        response, _ = self._remote_api(url=self.domain + CLUSTER_PERMISSION_CACHE)
        return self.string(self.user_roles_key) if response else None

    @property
    def cluster_groups(self):
        data = self.hash(self.CLUSTER_GROUPS)
        if data is not None:
            return {key: self._json_decode(value) for key, value in data.items()}

        response, _ = self._remote_api(url=self.domain + CLUSTER_GROUP_CACHE)

        if response:
            cache_data = self.hash(self.CLUSTER_GROUPS) or dict()
            return {key: self._json_decode(value) for key, value in cache_data.items()}

        return dict()

    @property
    def location_cluster(self):
        data = self.hash(self.LOCATION_CLUSTER)
        if data is not None:
            return data

        _, _ = self._remote_api(url=self.domain + LOCAL_CLUSTER_INFO)
        return self.hash(self.LOCATION_CLUSTER) or dict()

    @property
    def get_user_cluster_private_key(self):
        data = self.hash(self.user_private_key)
        if data is not None:
            return {key: self._json_decode(value) for key, value in data.items()}
        response, data = self._remote_api(url=self.domain + CLUSTER_PRIVATE_KEY)
        if not response or not data:
            return dict()

        cache_data = {
            item["cluster_id"]: dict(
                cluster_username=item["cluster_username"],
                private_key=item["private_key"],
                public_key=item["public_key"],
            )
            for item in data
        }
        RedisProxy.redis_connect.hmset(
            self.user_private_key, {cluster_id: json.dumps(key) for cluster_id, key in cache_data.items()}
        )
        return cache_data

    @property
    def all_groups_hosts(self):
        data = self.hash(self.GROUPS_HOSTS)
        if data is not None:
            return {key: self._json_decode(value) for key, value in data.items()}

        response, data = self._remote_api(url=self.domain + ALL_HOST_GROUP_MAP)
        if response and data:
            hash_data = {group_id: json.dumps(host_ids) for group_id, host_ids in data.items()}
            RedisProxy.redis_connect.hmset(
                self.GROUPS_HOSTS, {group_id: host_ids for group_id, host_ids in hash_data.items()}
            )
            RedisProxy.redis_connect.expire(self.GROUPS_HOSTS, 60)
        return data if response else dict()
