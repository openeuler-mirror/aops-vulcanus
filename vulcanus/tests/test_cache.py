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
        mock_client.hgetall.return_value = {"field": "value"}
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        result = cache.hash(TEST_KEY)
        self.assertEqual(result, {"field": "value"})

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
        mock_client.get.return_value = "test_value"
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        result = cache.string(TEST_KEY)
        self.assertEqual(result, "test_value")

    def test_string_not_exists(self):
        """Test string returns None when key doesn't exist."""
        mock_client = MagicMock()
        mock_client.exists.return_value = False
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        result = cache.string(TEST_KEY)
        self.assertIsNone(result)


class TestRedisCacheManageJsonDecode(unittest.TestCase):
    """Tests for RedisCacheManage _json_decode method."""

    def test_json_decode_valid(self):
        """Test _json_decode returns dict for valid JSON."""
        mock_client = MagicMock()
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        result = cache._json_decode(json.dumps({"key": "value"}))
        self.assertEqual(result["key"], "value")

    def test_json_decode_invalid(self):
        """Test _json_decode returns original string for invalid JSON."""
        mock_client = MagicMock()
        cache = RedisCacheManage(domain=DOMAIN, redis_client=mock_client)
        result = cache._json_decode("not json")
        self.assertEqual(result, "not json")


if __name__ == "__main__":
    unittest.main()
