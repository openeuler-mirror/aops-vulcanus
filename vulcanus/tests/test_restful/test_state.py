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
Description: unit tests for restful/resp/state.py
"""
import unittest

from vulcanus.restful.resp.state import (
    SUCCEED,
    PARTIAL_SUCCEED,
    SERVER_ERROR,
    PARAM_ERROR,
    HTTP_CONNECT_ERROR,
    DATABASE_CONNECT_ERROR,
    TOKEN_ERROR,
    TOKEN_EXPIRE,
    PERMESSION_ERROR,
    NO_DATA,
    WRONG_DATA,
)

SUCCEED_VAL = "Succeed"
PARTIAL_VAL = "Partial.Succeed"
SERVER_ERR_VAL = "Server.Error"
PARAM_ERR_VAL = "Param.Error"
HTTP_ERR_VAL = "Http.Connect.Error"
DB_ERR_VAL = "Database.Connect.Error"
TOKEN_ERR_VAL = "Token.Error"
TOKEN_EXPIRE_VAL = "Token.Expire"
PERM_ERR_VAL = "Permission.Error"
NO_DATA_VAL = "No.Data"
WRONG_DATA_VAL = "Wrong.Data"


class TestStateConstants(unittest.TestCase):
    """Tests for state.py constants."""

    def test_succeed(self):
        """Test SUCCEED constant value."""
        self.assertEqual(SUCCEED, SUCCEED_VAL)

    def test_partial_succeed(self):
        """Test PARTIAL_SUCCEED constant value."""
        self.assertEqual(PARTIAL_SUCCEED, PARTIAL_VAL)

    def test_server_error(self):
        """Test SERVER_ERROR constant value."""
        self.assertEqual(SERVER_ERROR, SERVER_ERR_VAL)

    def test_param_error(self):
        """Test PARAM_ERROR constant value."""
        self.assertEqual(PARAM_ERROR, PARAM_ERR_VAL)

    def test_http_connect_error(self):
        """Test HTTP_CONNECT_ERROR constant value."""
        self.assertEqual(HTTP_CONNECT_ERROR, HTTP_ERR_VAL)

    def test_database_connect_error(self):
        """Test DATABASE_CONNECT_ERROR constant value."""
        self.assertEqual(DATABASE_CONNECT_ERROR, DB_ERR_VAL)

    def test_token_error(self):
        """Test TOKEN_ERROR constant value."""
        self.assertEqual(TOKEN_ERROR, TOKEN_ERR_VAL)

    def test_token_expire(self):
        """Test TOKEN_EXPIRE constant value."""
        self.assertEqual(TOKEN_EXPIRE, TOKEN_EXPIRE_VAL)

    def test_permession_error(self):
        """Test PERMESSION_ERROR constant value."""
        self.assertEqual(PERMESSION_ERROR, PERM_ERR_VAL)

    def test_no_data(self):
        """Test NO_DATA constant value."""
        self.assertEqual(NO_DATA, NO_DATA_VAL)

    def test_wrong_data(self):
        """Test WRONG_DATA constant value."""
        self.assertEqual(WRONG_DATA, WRONG_DATA_VAL)


if __name__ == "__main__":
    unittest.main()
