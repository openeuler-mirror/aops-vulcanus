# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2024. All rights reserved.
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
Description: unit tests for exceptions/synchronize_exception.py
"""
import unittest

from vulcanus.exceptions.synchronize_exception import SynchronizeError

ERR_MSG = "sync failed"


class TestSynchronizeError(unittest.TestCase):
    """Tests for SynchronizeError class."""

    def test_init(self):
        """Test SynchronizeError stores error message."""
        err = SynchronizeError(ERR_MSG)
        self.assertEqual(err.error, ERR_MSG)

    def test_str(self):
        """Test SynchronizeError str representation."""
        err = SynchronizeError(ERR_MSG)
        self.assertIn(ERR_MSG, str(err))

    def test_is_exception(self):
        """Test SynchronizeError is an Exception."""
        err = SynchronizeError(ERR_MSG)
        self.assertIsInstance(err, Exception)

    def test_catch_as_exception(self):
        """Test SynchronizeError can be caught as Exception."""
        with self.assertRaises(Exception):
            raise SynchronizeError(ERR_MSG)


if __name__ == "__main__":
    unittest.main()
