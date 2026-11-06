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
import stat
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import logging

from vulcanus.log.log import LOG_DIR_MODE, _prepare_log_dir

LOG_DIR = "log_dir"
LOG_LEVEL = "log_level"
MAX_BYTES = "max_bytes"
BACKUP_COUNT = "backup_count"


class TestLoggerCheckInteger(unittest.TestCase):
    """Tests for Logger parameter validation via check()."""

    def test_check_valid_params(self):
        """Test Logger does not raise for valid integer params."""
        from vulcanus.log.log import Logger
        mock_config = MagicMock()
        mock_config.log.log_dir = tempfile.mkdtemp()
        mock_config.log.log_level = "INFO"
        mock_config.log.max_bytes = 1024
        mock_config.log.backup_count = 1
        with patch("vulcanus.log.log.configuration", mock_config):
            logger_obj = Logger()
            logger_obj.check()

    def test_check_zero_max_bytes(self):
        """Test Logger raises ValueError for zero max_bytes."""
        from vulcanus.log.log import Logger
        mock_config = MagicMock()
        mock_config.log.log_dir = tempfile.mkdtemp()
        mock_config.log.log_level = "INFO"
        mock_config.log.max_bytes = 0
        mock_config.log.backup_count = 1
        with patch("vulcanus.log.log.configuration", mock_config):
            with self.assertRaises(ValueError):
                Logger()

    def test_check_negative_backup(self):
        """Test Logger raises ValueError for negative backup_count."""
        from vulcanus.log.log import Logger
        mock_config = MagicMock()
        mock_config.log.log_dir = tempfile.mkdtemp()
        mock_config.log.log_level = "INFO"
        mock_config.log.max_bytes = 1024
        mock_config.log.backup_count = -1
        with patch("vulcanus.log.log.configuration", mock_config):
            with self.assertRaises(ValueError):
                Logger()

    def test_check_non_int_max_bytes(self):
        """Test Logger raises ValueError for non-int max_bytes."""
        from vulcanus.log.log import Logger
        mock_config = MagicMock()
        mock_config.log.log_dir = tempfile.mkdtemp()
        mock_config.log.log_level = "INFO"
        mock_config.log.max_bytes = "not_int"
        mock_config.log.backup_count = 1
        with patch("vulcanus.log.log.configuration", mock_config):
            with self.assertRaises(ValueError):
                Logger()


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


class TestPrepareLogDir(unittest.TestCase):
    """Tests for log directory preparation."""

    def test_existing_directory_is_normalized_to_log_dir_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = os.path.join(temp_dir, "aops")
            os.mkdir(log_dir)
            os.chmod(log_dir, 0o644)

            _prepare_log_dir(log_dir)

            self.assertEqual(stat.S_IMODE(os.stat(log_dir).st_mode), LOG_DIR_MODE)

    def test_new_directory_uses_log_dir_mode_regardless_of_umask(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = os.path.join(temp_dir, "aops")
            old_umask = os.umask(0o077)
            try:
                _prepare_log_dir(log_dir)
            finally:
                os.umask(old_umask)

            self.assertEqual(stat.S_IMODE(os.stat(log_dir).st_mode), LOG_DIR_MODE)

    def test_chmod_failure_does_not_abort_directory_preparation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = os.path.join(temp_dir, "aops")
            os.mkdir(log_dir)
            os.chmod(log_dir, 0o644)
            with self.assertLogs("vulcanus.log.log", level="WARNING"):
                with patch("vulcanus.log.log.os.chmod", side_effect=PermissionError("denied")):
                    _prepare_log_dir(log_dir)

            self.assertTrue(os.path.isdir(log_dir))


if __name__ == "__main__":
    unittest.main()
