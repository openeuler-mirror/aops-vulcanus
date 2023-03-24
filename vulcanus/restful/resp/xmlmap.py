#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import os
import threading

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et


class XmlParse:
    """
    Parse the default response body file and return the request response in a uniform manner
    """

    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not hasattr(cls, "__instance"):
                cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.xml = None

    def _load_xml(self, xml_path):
        """
        Load the contents of the xml file

        Args:
            xml_path: xml文件的路径

        """
        if not xml_path:
            self.xml = None
            raise ValueError("The xml file path was not specified")
        xml_path = os.path.join(os.path.dirname(__file__), xml_path)
        try:
            self.xml = et.parse(xml_path)
        except Exception:
            raise ValueError(
                f"Content of the xml file is incorrect: {xml_path}")

    def clear_xml(self):
        self.xml = None

    @property
    def root(self):
        return self.xml.getroot()

    def _todict(self, tag):
        return {child.tag: child.text for child in tag.findall("*")}

    def content(self, label):
        if not self.xml:
            self._load_xml("map.xml")
        tag = self.root.find("./code/[@label='%s']" % label)
        if tag is None:
            return tag

        return self._todict(tag)


class Response:
    """
    Get the standard response content by default code
    """

    xml = XmlParse()

    def __init__(self, label, message=None):
        self._label = label
        self.response_body = dict(message=message)

    def _response_content(self, label):
        body = Response.xml.content(label)
        if not body:
            raise ValueError("An incorrect code value was passed")

        body["label"] = label
        return body

    @property
    def response(self):
        """
        The content of the http response

        Returns:
            response_body: e.g
                {
                    "code": int,
                    "message": str,
                    "label": str
                }
        """
        self._set_body(self._response_content(self._label))
        return self.response_body

    def _set_body(self, body, zh=False):

        if "message" not in self.response_body or self.response_body["message"] is None:
            self.response_body["message"] = (
                body["message_zh"] if zh else body["message_en"]
            )
        self.response_body["code"] = body["status_code"]
        self.response_body["label"] = body["label"]

    def body(self, label: str, zh: bool = False, **kwargs):
        """
        Get information about the response body

        Args:
            label: Constant tag for the response
            zh: Display in Chinese or English
            kwargs: e.g
                {
                    "data": Content of response
                }
        """
        if "message" not in kwargs:
            self.response_body["message"] = None

        if "data" in kwargs and not kwargs["data"]:
            del kwargs["data"]

        self.response_body = kwargs
        self._set_body(self._response_content(label), zh)
        return self.response_body
