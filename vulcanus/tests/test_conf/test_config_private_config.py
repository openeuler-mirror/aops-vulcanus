#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2024-2024. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import logging
import os
import tempfile
import unittest
from unittest import mock

from vulcanus.conf import Config


class TestConfigPrivateFile(unittest.TestCase):
    def test_private_config_file_is_optional(self):
        file_descriptor, config_path = tempfile.mkstemp(suffix=".ini")
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as config_file:
                config_file.write("[test]\nkey=1\n")

            with mock.patch(
                "vulcanus.conf.PRIVATE_INDIVIDUATION_CONFIG", "/nonexistent/aops-private.ini"
            ):
                with self.assertLogs("vulcanus.conf", level="DEBUG") as captured:
                    config = Config(config_path)

            self.assertEqual(config.test["KEY"], 1)
            self.assertTrue(any("not found" in message for message in captured.output))
            self.assertTrue(
                all(record.levelno == logging.DEBUG for record in captured.records)
            )
        finally:
            os.remove(config_path)


if __name__ == "__main__":
    unittest.main()
