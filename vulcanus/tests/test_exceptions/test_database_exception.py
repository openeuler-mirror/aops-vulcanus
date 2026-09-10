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
Description: unit tests for exceptions/database_exception.py
"""
import unittest

from vulcanus.exceptions.database_exception import DatabaseError, DatabaseConnectionFailed

ERR_MSG = "test error"
CONN_ERR_MSG = "connection timeout"


class TestDatabaseError(unittest.TestCase):
    """Tests for DatabaseError class."""

    def test_init(self):
        """Test DatabaseError stores error message."""
        err = DatabaseError(ERR_MSG)
        self.assertEqual(err.error, ERR_MSG)

    def test_str(self):
        """Test DatabaseError str representation."""
        err = DatabaseError(ERR_MSG)
        self.assertIn(ERR_MSG, str(err))

    def test_is_exception(self):
        """Test DatabaseError is an Exception."""
        err = DatabaseError(ERR_MSG)
        self.assertIsInstance(err, Exception)


class TestDatabaseConnectionFailed(unittest.TestCase):
    """Tests for DatabaseConnectionFailed class."""

    def test_init(self):
        """Test DatabaseConnectionFailed stores error message."""
        err = DatabaseConnectionFailed(CONN_ERR_MSG)
        self.assertEqual(err.error, CONN_ERR_MSG)

    def test_str(self):
        """Test DatabaseConnectionFailed str representation."""
        err = DatabaseConnectionFailed(CONN_ERR_MSG)
        self.assertIn(CONN_ERR_MSG, str(err))

    def test_is_database_error(self):
        """Test DatabaseConnectionFailed is a DatabaseError."""
        err = DatabaseConnectionFailed(CONN_ERR_MSG)
        self.assertIsInstance(err, DatabaseError)

    def test_catch_as_exception(self):
        """Test DatabaseConnectionFailed can be caught as Exception."""
        with self.assertRaises(Exception):
            raise DatabaseConnectionFailed(CONN_ERR_MSG)


if __name__ == "__main__":
    unittest.main()
