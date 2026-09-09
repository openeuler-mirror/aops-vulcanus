# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2023. All rights reserved.
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
Description: unit tests for log/log.py
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import logging


class TestLoggerCheckInteger(unittest.TestCase):
    """Tests for Logger.__check_integer static method."""

    def test_check_integer_valid(self):
        """Test __check_integer does not raise for valid int."""
        from vulcanus.log.log import Logger
        Logger.__check_integer(1024, "test_param")

    def test_check_integer_zero(self):
        """Test __check_integer raises ValueError for zero."""
        from vulcanus.log.log import Logger
        with self.assertRaises(ValueError):
            Logger.__check_integer(0, "test_param")

    def test_check_integer_negative(self):
        """Test __check_integer raises ValueError for negative."""
        from vulcanus.log.log import Logger
        with self.assertRaises(ValueError):
            Logger.__check_integer(-1, "test_param")

    def test_check_integer_non_int(self):
        """Test __check_integer raises ValueError for non-int."""
        from vulcanus.log.log import Logger
        with self.assertRaises(ValueError):
            Logger.__check_integer("not_int", "test_param")


class TestLoggerGetLogger(unittest.TestCase):
    """Tests for Logger.get_logger method."""

    def test_get_logger_returns_logger(self):
        """Test get_logger returns a Logger instance."""
        from vulcanus.log.log import Logger
        mock_config = MagicMock()
        mock_config.log.log_dir = tempfile.mkdtemp()
        mock_config.log.log_level = "INFO"
        mock_config.log.max_bytes = 1024
        mock_config.log.backup_count = 1
        with patch("vulcanus.log.log.configuration", mock_config):
            logger_obj = Logger()
            logger = logger_obj.get_logger()
            self.assertIsNotNone(logger)
            self.assertEqual(logger.level, logging.INFO)


if __name__ == "__main__":
    unittest.main()
