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
Description: unit tests for database/helper.py
"""
import time
import unittest
from unittest.mock import MagicMock

from vulcanus.database.helper import (
    make_mysql_engine_url,
    timestamp_datetime,
    timestr_unix,
    judge_return_code,
    combine_return_codes,
    sort_and_page,
)
from vulcanus.restful.resp.state import PARTIAL_SUCCEED, SUCCEED

TEST_HOST = "127.0.0.1"
TEST_PORT = "3306"
TEST_USER = "root"
TEST_PASS = "password"
TEST_DB = "testdb"
UNIX_TS = 1705312200


class TestMakeMysqlEngineUrl(unittest.TestCase):
    """Tests for make_mysql_engine_url function."""

    def test_with_credentials(self):
        """Test make_mysql_engine_url with username and password."""
        config = MagicMock()
        config.mysql.host = TEST_HOST
        config.mysql.port = TEST_PORT
        config.mysql.username = TEST_USER
        config.mysql.password = TEST_PASS
        config.mysql.database = TEST_DB
        url = make_mysql_engine_url(config)
        self.assertIn(TEST_USER, url)
        self.assertIn(TEST_HOST, url)
        self.assertIn(TEST_DB, url)

    def test_without_credentials(self):
        """Test make_mysql_engine_url without username/password."""
        config = MagicMock()
        config.mysql.host = TEST_HOST
        config.mysql.port = TEST_PORT
        config.mysql.username = ""
        config.mysql.password = ""
        config.mysql.database = TEST_DB
        url = make_mysql_engine_url(config)
        self.assertNotIn(TEST_USER, url)
        self.assertIn(TEST_HOST, url)


class TestTimestampDatetime(unittest.TestCase):
    """Tests for timestamp_datetime function."""

    def test_timestamp_to_datetime(self):
        """Test timestamp_datetime converts unix time to formatted string."""
        result = timestamp_datetime(UNIX_TS)
        self.assertIn("2024", result)

    def test_timestamp_datetime_format(self):
        """Test timestamp_datetime returns correct format."""
        result = timestamp_datetime(0)
        self.assertIn("1970", result)


class TestTimestrUnix(unittest.TestCase):
    """Tests for timestr_unix function."""

    def test_timestr_to_unix(self):
        """Test timestr_unix converts formatted time to unix timestamp."""
        time_str = "2024-01-15T10:30:00.000000+0800"
        result = timestr_unix(time_str)
        self.assertIsInstance(result, int)


class TestJudgeReturnCode(unittest.TestCase):
    """Tests for judge_return_code function."""

    def test_succeed(self):
        """Test judge_return_code returns SUCCEED when only succeed_list."""
        result = {"succeed_list": ["item1"], "fail_list": []}
        self.assertEqual(judge_return_code(result, SUCCEED), SUCCEED)

    def test_partial(self):
        """Test judge_return_code returns PARTIAL_SUCCEED when both lists."""
        result = {"succeed_list": ["item1"], "fail_list": ["item2"]}
        self.assertEqual(judge_return_code(result, SUCCEED), PARTIAL_SUCCEED)

    def test_fail_only(self):
        """Test judge_return_code returns default when only fail_list."""
        result = {"fail_list": ["item1"]}
        self.assertEqual(judge_return_code(result, SUCCEED), SUCCEED)

    def test_empty(self):
        """Test judge_return_code returns SUCCEED for empty result."""
        result = {}
        self.assertEqual(judge_return_code(result, SUCCEED), SUCCEED)


class TestCombineReturnCodes(unittest.TestCase):
    """Tests for combine_return_codes function."""

    def test_all_succeed(self):
        """Test combine_return_codes returns SUCCEED when all succeed."""
        self.assertEqual(combine_return_codes(SUCCEED, SUCCEED, SUCCEED), SUCCEED)

    def test_partial_present(self):
        """Test combine_return_codes returns PARTIAL_SUCCEED when present."""
        self.assertEqual(combine_return_codes(SUCCEED, SUCCEED, PARTIAL_SUCCEED), PARTIAL_SUCCEED)

    def test_mixed(self):
        """Test combine_return_codes returns PARTIAL_SUCCEED for mixed codes."""
        self.assertEqual(combine_return_codes(SUCCEED, SUCCEED, 500), PARTIAL_SUCCEED)

    def test_all_fail(self):
        """Test combine_return_codes returns default when all fail."""
        self.assertEqual(combine_return_codes(SUCCEED, 500, 500), SUCCEED)


class TestSortAndPage(unittest.TestCase):
    """Tests for sort_and_page function."""

    def test_empty_query(self):
        """Test sort_and_page with empty query returns empty."""
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        result, total = sort_and_page(mock_query, None, None, None, None)
        self.assertEqual(total, 1)


if __name__ == "__main__":
    unittest.main()
