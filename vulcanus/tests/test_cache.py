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
"""
Description: unit tests for cache.py
"""
import json
import unittest
from unittest.mock import patch, MagicMock

from vulcanus.cache import RedisCacheManage

DOMAIN = "localhost:8080"
TEST_KEY = "test_key"
TEST_USERNAME = "testuser"
FIELD = "field"
VAL = "value"
TEST_VAL = "test_value"
NOT_JSON = "not json"


class TestRedisCacheManageInit(unittest.TestCase):
    """Tests for RedisCacheManage initialization."""

    def test_init_with_client(self):
        """Test RedisCacheManage init with redis client."""
        mock_client = MagicMock()
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        self.assertEqual(cache.client, mock_client)

    def test_init_without_client(self):
        """Test RedisCacheManage init uses RedisProxy."""
        with patch("vulcanus.cache.RedisProxy") as mock_proxy:
            mock_proxy.redis_connect = MagicMock()
            cache = RedisCacheManage(domain=DOMAIN)
            self.assertIsNotNone(cache.client)

    def test_user_clusters_key(self):
        """Test user_clusters_key property."""
        mock_client = MagicMock()
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client, username=TEST_USERNAME)
        self.assertEqual(cache.user_clusters_key, TEST_USERNAME + "_clusters")

    def test_user_groups_key(self):
        """Test user_groups_key property."""
        mock_client = MagicMock()
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client, username=TEST_USERNAME)
        self.assertEqual(cache.user_groups_key, TEST_USERNAME + "_group_hosts")


class TestRedisCacheManageHash(unittest.TestCase):
    """Tests for RedisCacheManage hash method."""

    def test_hash_exists(self):
        """Test hash returns data when key exists."""
        mock_client = MagicMock()
        mock_client.exists.return_value = True
        mock_client.hgetall.return_value = {FIELD: VAL}
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        result = cache.hash(TEST_KEY)
        self.assertEqual(result, {FIELD: VAL})

    def test_hash_not_exists(self):
        """Test hash returns None when key doesn't exist."""
        mock_client = MagicMock()
        mock_client.exists.return_value = False
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        result = cache.hash(TEST_KEY)
        self.assertIsNone(result)


class TestRedisCacheManageString(unittest.TestCase):
    """Tests for RedisCacheManage string method."""

    def test_string_exists(self):
        """Test string returns value when key exists."""
        mock_client = MagicMock()
        mock_client.exists.return_value = True
        mock_client.get.return_value = TEST_VAL
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        result = cache.string(TEST_KEY)
        self.assertEqual(result, TEST_VAL)

    def test_string_not_exists(self):
        """Test string returns None when key doesn't exist."""
        mock_client = MagicMock()
        mock_client.exists.return_value = False
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        result = cache.string(TEST_KEY)
        self.assertIsNone(result)


class TestRedisCacheManageClusters(unittest.TestCase):
    """Tests for RedisCacheManage clusters property."""

    def test_clusters_empty(self):
        """Test clusters returns empty dict when no data."""
        mock_client = MagicMock()
        mock_client.exists.return_value = False
        mock_client.get.return_value = (None, None)
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        with patch.object(cache, '_remote_api', return_value=(False, None)):
            result = cache.clusters
            self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
