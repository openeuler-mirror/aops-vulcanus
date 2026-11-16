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
import unittest

from vulcanus.conf.constant import CONFIG_ROOT_PATH, SERVICE_CUSTOM_CONFIG_PATH


class TestConstant(unittest.TestCase):
    def test_service_custom_config_path_is_under_config_root(self):
        self.assertEqual(SERVICE_CUSTOM_CONFIG_PATH, f"{CONFIG_ROOT_PATH}/services")


if __name__ == "__main__":
    unittest.main()
