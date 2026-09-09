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
Description: unit tests for token.py
"""
import time
import unittest
from unittest.mock import patch, MagicMock

from vulcanus.token import get_timedelta, generate_token, decode_token

TEST_USER = "testuser"
TEST_KEY = "secret_key_for_testing"


class TestGetTimedelta(unittest.TestCase):
    """Tests for get_timedelta function."""

    def test_get_timedelta_default(self):
        """Test get_timedelta returns future time with default 20 minutes."""
        result = get_timedelta()
        now = int(time.time())
        self.assertGreater(result, now)

    def test_get_timedelta_zero(self):
        """Test get_timedelta with zero minutes returns current time."""
        result = get_timedelta(0)
        now = int(time.time())
        self.assertGreaterEqual(result, now - 2)

    def test_get_timedelta_positive(self):
        """Test get_timedelta with positive minutes returns future time."""
        result = get_timedelta(60)
        now = int(time.time())
        self.assertGreater(result, now)


class TestGenerateToken(unittest.TestCase):
    """Tests for generate_token function."""

    @patch("vulcanus.token.configuration")
    def test_generate_token_success(self, mock_config):
        """Test generate_token returns a token string."""
        mock_config.individuation.private_key = TEST_KEY
        token = generate_token(TEST_USER)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)

    @patch("vulcanus.token.configuration")
    def test_generate_token_with_aud(self, mock_config):
        """Test generate_token with aud parameter."""
        mock_config.individuation.private_key = TEST_KEY
        token = generate_token(TEST_USER, aud="test_audience")
        self.assertIsInstance(token, str)

    def test_generate_token_empty_identifier(self):
        """Test generate_token with empty identifier returns ValueError."""
        result = generate_token("")
        self.assertIsInstance(result, ValueError)


class TestDecodeToken(unittest.TestCase):
    """Tests for decode_token function."""

    @patch("vulcanus.token.configuration")
    def test_decode_token_success(self, mock_config):
        """Test decode_token returns decoded payload."""
        mock_config.individuation.private_key = TEST_KEY
        token = generate_token(TEST_USER)
        payload = decode_token(token)
        self.assertEqual(payload["sub"], TEST_USER)

    def test_decode_token_empty(self):
        """Test decode_token with empty token raises ValueError."""
        with self.assertRaises(ValueError):
            decode_token("")

    def test_decode_token_invalid(self):
        """Test decode_token with invalid token raises ValueError."""
        with self.assertRaises(ValueError):
            decode_token("invalid.token.value")


if __name__ == "__main__":
    unittest.main()
