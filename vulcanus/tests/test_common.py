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
Description: unit tests for common.py
"""
import json
import os
import tempfile
import unittest

from vulcanus.common import ValidateUtils, TimeUtils, ConfigFileParse, hash_value

TEST_PATH = "/tmp/test_common_file"
TEST_TIME = "20240115-10:30:00"
HASH_INPUT = "hello"


class TestValidateUtils(unittest.TestCase):
    """Tests for ValidateUtils class."""

    def test_compare_two_object_equal(self):
        """Test compare_two_object returns True for equal objects."""
        self.assertTrue(ValidateUtils.compare_two_object({"a": 1}, {"a": 1}))

    def test_compare_two_object_not_equal(self):
        """Test compare_two_object returns False for different objects."""
        self.assertFalse(ValidateUtils.compare_two_object({"a": 1}, {"a": 2}))

    def test_validate_path_nonexistent(self):
        """Test validate_path returns False for non-existent path."""
        self.assertFalse(ValidateUtils.validate_path("/nonexistent/path"))

    def test_validate_path_valid(self):
        """Test validate_path returns True for valid file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            f.flush()
            try:
                self.assertTrue(ValidateUtils.validate_path(f.name))
            finally:
                os.unlink(f.name)

    def test_validate_path_directory(self):
        """Test validate_path returns False for directory when file=True."""
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(ValidateUtils.validate_path(d, file=True))

    def test_validate_time_valid(self):
        """Test validate_time returns True for valid time string."""
        self.assertTrue(ValidateUtils.validate_time(TEST_TIME, TimeUtils.TIME_FORMAT))

    def test_validate_time_invalid(self):
        """Test validate_time returns False for invalid time string."""
        self.assertFalse(ValidateUtils.validate_time("not-a-time", TimeUtils.TIME_FORMAT))


class TestTimeUtils(unittest.TestCase):
    """Tests for TimeUtils class."""

    def test_time_transfer_none_start(self):
        """Test time_transfer with None start_time."""
        result = TimeUtils.time_transfer(None, TEST_TIME)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 0)

    def test_time_transfer_none_end(self):
        """Test time_transfer with None end_time."""
        result = TimeUtils.time_transfer(TEST_TIME, None)
        self.assertIsNotNone(result)
        self.assertEqual(result[1], int(__import__("time").time()))

    def test_time_transfer_invalid_format(self):
        """Test time_transfer returns None for invalid format."""
        result = TimeUtils.time_transfer("invalid", "invalid")
        self.assertIsNone(result)


class TestConfigFileParse(unittest.TestCase):
    """Tests for ConfigFileParse class."""

    def test_read_yaml_none(self):
        """Test read_yaml_config_file returns None for None input."""
        self.assertIsNone(ConfigFileParse.read_yaml_config_file(None))

    def test_read_json_none(self):
        """Test read_json_config_file returns None for None input."""
        self.assertIsNone(ConfigFileParse.read_json_config_file(None))

    def test_read_xml_none(self):
        """Test read_xml_config_file returns None for None input."""
        self.assertIsNone(ConfigFileParse.read_xml_config_file(None))

    def test_read_json_valid(self):
        """Test read_json_config_file reads valid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"key": "value"}, f)
            f.flush()
            try:
                result = ConfigFileParse.read_json_config_file(f.name)
                self.assertEqual(result["key"], "value")
            finally:
                os.unlink(f.name)

    def test_read_json_invalid(self):
        """Test read_json_config_file returns None for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not json")
            f.flush()
            try:
                result = ConfigFileParse.read_json_config_file(f.name)
                self.assertIsNone(result)
            finally:
                os.unlink(f.name)

    def test_read_yaml_valid(self):
        """Test read_yaml_config_file reads valid YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("key: value\n")
            f.flush()
            try:
                result = ConfigFileParse.read_yaml_config_file(f.name)
                self.assertEqual(result["key"], "value")
            finally:
                os.unlink(f.name)


class TestHashValue(unittest.TestCase):
    """Tests for hash_value function."""

    def test_hash_value_returns_string(self):
        """Test hash_value returns a string."""
        result = hash_value("test")
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 32)

    def test_hash_value_empty(self):
        """Test hash_value raises ValueError for empty string."""
        with self.assertRaises(ValueError):
            hash_value("")

    def test_hash_value_consistent(self):
        """Test hash_value returns same hash for same input."""
        h1 = hash_value(HASH_INPUT)
        h2 = hash_value(HASH_INPUT)
        self.assertEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
