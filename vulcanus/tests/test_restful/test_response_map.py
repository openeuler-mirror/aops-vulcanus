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
import xml.etree.ElementTree as ET
from pathlib import Path

from vulcanus.restful.resp import state


class TestResponseMap(unittest.TestCase):
    def test_status_labels_and_map_are_consistent(self):
        map_path = Path(__file__).resolve().parents[2] / "restful" / "resp" / "map.xml"
        map_labels = [code.get("label") for code in ET.parse(map_path).getroot().findall("code")]
        state_labels = {
            value for name, value in vars(state).items() if name.isupper() and isinstance(value, str)
        }

        self.assertEqual(sorted(state_labels - set(map_labels)), [])
        self.assertEqual(sorted(set(map_labels) - state_labels), [])
        self.assertEqual(len(map_labels), len(set(map_labels)))


if __name__ == "__main__":
    unittest.main()
