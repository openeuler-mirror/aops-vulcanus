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
Description: unit tests for conf/default_config.py
"""
import os
import unittest

from vulcanus.conf.default_config import log, individuation, email

LOG_DIR = "LOG_DIR"
LOG_LEVEL = "LOG_LEVEL"
MAX_BYTES = "MAX_BYTES"
BACKUP_COUNT = "BACKUP_COUNT"
GITEE_CLIENT_ID = "GITEE_CLIENT_ID"
GITEE_CLIENT_SECRET = "GITEE_CLIENT_SECRET"
SERVER = "SERVER"
PORT = "PORT"
SMTP_SSL = "SMTP_SSL"
ENABLED = "ENABLED"


class TestLogConfig(unittest.TestCase):
    """Tests for log configuration dict."""

    def test_log_dir_is_var_log(self):
        """Test LOG_DIR points to /var/log/aops."""
        self.assertIn("/var", log[LOG_DIR])
        self.assertIn("aops", log[LOG_DIR])

    def test_log_level_info(self):
        """Test LOG_LEVEL is INFO."""
        self.assertEqual(log[LOG_LEVEL], "INFO")

    def test_max_bytes_positive(self):
        """Test MAX_BYTES is positive."""
        self.assertGreater(log[MAX_BYTES], 0)

    def test_backup_count_positive(self):
        """Test BACKUP_COUNT is positive."""
        self.assertGreater(log[BACKUP_COUNT], 0)


class TestIndividuationConfig(unittest.TestCase):
    """Tests for individuation configuration dict."""

    def test_gitee_client_id_exists(self):
        """Test GITEE_CLIENT_ID key exists."""
        self.assertIn(GITEE_CLIENT_ID, individuation)

    def test_gitee_client_secret_exists(self):
        """Test GITEE_CLIENT_SECRET key exists."""
        self.assertIn(GITEE_CLIENT_SECRET, individuation)

    def test_redirect_url_exists(self):
        """Test REDIRECT_URL key exists."""
        self.assertIn("REDIRECT_URL", individuation)


class TestEmailConfig(unittest.TestCase):
    """Tests for email configuration dict."""

    def test_email_server_exists(self):
        """Test SERVER key exists."""
        self.assertIn(SERVER, email)

    def test_email_port(self):
        """Test PORT is 25."""
        self.assertEqual(email[PORT], 25)

    def test_email_smtp_ssl_false(self):
        """Test SMTP_SSL is False."""
        self.assertFalse(email[SMTP_SSL])

    def test_email_enabled_false(self):
        """Test ENABLED is False."""
        self.assertFalse(email[ENABLED])


if __name__ == "__main__":
    unittest.main()
