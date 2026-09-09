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
Description: unit tests for send_email.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vulcanus.send_email import Email

SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 465
SENDER = "test@example.com"
AUTH_CODE = "test_auth_code"
RECEIVERS = ["receiver@example.com"]


class TestEmailInit(unittest.TestCase):
    """Tests for Email initialization."""

    def test_init(self):
        """Test Email initializes with server, port, sender, auth code."""
        email = Email(SMTP_SERVER, SMTP_PORT, SENDER, AUTH_CODE)
        self.assertEqual(email.sender, SENDER)
        self.assertEqual(email.server, SMTP_SERVER)
        self.assertEqual(email.port, SMTP_PORT)
        self.assertEqual(email.authorization_code, AUTH_CODE)


class TestEmailSend(unittest.TestCase):
    """Tests for Email.send method."""

    @patch("vulcanus.send_email.smtplib.SMTP_SSL")
    def test_send_success_ssl(self, mock_smtp_ssl):
        """Test send returns True on success with SSL."""
        mock_server = MagicMock()
        mock_smtp_ssl.return_value = mock_server
        email = Email(SMTP_SERVER, SMTP_PORT, SENDER, AUTH_CODE)
        message = MagicMock()
        message.as_string.return_value = "test message"
        result, _ = email.send(RECEIVERS, message, smtp_ssl=True)
        self.assertTrue(result)
        mock_server.sendmail.assert_called_once()

    @patch("vulcanus.send_email.smtplib.SMTP")
    def test_send_success(self, mock_smtp):
        """Test send returns True on success without SSL."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        email = Email(SMTP_SERVER, SMTP_PORT, SENDER, AUTH_CODE)
        message = MagicMock()
        message.as_string.return_value = "test message"
        result, _ = email.send(RECEIVERS, message)
        self.assertTrue(result)

    @patch("vulcanus.send_email.smtplib.SMTP_SSL")
    def test_send_smtp_error(self, mock_smtp_ssl):
        """Test send returns False on SMTP error."""
        import smtplib
        mock_server = MagicMock()
        mock_server.sendmail.side_effect = smtplib.SMTPException("error")
        mock_smtp_ssl.return_value = mock_server
        email = Email(SMTP_SERVER, SMTP_PORT, SENDER, AUTH_CODE)
        message = MagicMock()
        message.as_string.return_value = "test message"
        result, error = email.send(RECEIVERS, message, smtp_ssl=True)
        self.assertFalse(result)


class TestEmailTurnDataToTableHtml(unittest.TestCase):
    """Tests for Email.turn_data_to_table_html static method."""

    def test_turn_data_to_table_html(self):
        """Test turn_data_to_table_html generates correct HTML."""
        thead = ["col1", "col2"]
        tbody = [["val1", "val2"], ["val3", "val4"]]
        result = Email.turn_data_to_table_html(thead, tbody)
        self.assertIn("<table", result)
        self.assertIn("col1", result)
        self.assertIn("val1", result)
        self.assertIn("</table>", result)

    def test_turn_data_to_table_html_empty(self):
        """Test turn_data_to_table_html with empty data."""
        result = Email.turn_data_to_table_html([], [])
        self.assertIn("<table", result)


if __name__ == "__main__":
    unittest.main()
