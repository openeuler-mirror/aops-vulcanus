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
Description: unit tests for restful/resp/xmlmap.py
"""
import unittest

from vulcanus.restful.resp.xmlmap import XmlParse, Response

LABEL = "Succeed"


class TestXmlParse(unittest.TestCase):
    """Tests for XmlParse class."""

    def test_singleton(self):
        """Test XmlParse is a singleton."""
        a = XmlParse()
        b = XmlParse()
        self.assertIs(a, b)

    def test_clear_xml(self):
        """Test clear_xml sets xml to None."""
        parser = XmlParse()
        parser.clear_xml()
        self.assertIsNone(parser.xml)

    def test_content_without_xml(self):
        """Test content triggers load_xml when xml is None."""
        parser = XmlParse()
        parser.clear_xml()
        with self.assertRaises(ValueError):
            parser.content(LABEL)


class TestResponse(unittest.TestCase):
    """Tests for Response class."""

    def test_response_init_with_message(self):
        """Test Response initializes with message."""
        resp = Response(LABEL, message="test message")
        self.assertEqual(resp.response_body["message"], "test message")

    def test_response_init_default_body(self):
        """Test Response initializes with default response body."""
        resp = Response(LABEL)
        self.assertIsInstance(resp.response_body, dict)


if __name__ == "__main__":
    unittest.main()
