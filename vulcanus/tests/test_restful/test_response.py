# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Description: unit tests for restful/response.py
"""
import json
import unittest
from unittest.mock import patch, MagicMock

from vulcanus.restful.response import BaseResponse
from vulcanus.restful.resp import state

TEST_URL = "http://localhost:8080/api/test"
TEST_DATA = {"key": "value"}
TEST_TOKEN = "test_token_123"
TEST_USERNAME = "testuser"


class TestBaseResponseGetResponse(unittest.TestCase):
    """Tests for BaseResponse.get_response static method."""

    @patch("vulcanus.restful.response.requests.request")
    def test_get_response_success(self, mock_request):
        """Test get_response returns parsed JSON on success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"code": 0, "data": "ok"})
        mock_request.return_value = mock_response
        result = BaseResponse.get_response("GET", TEST_URL)
        self.assertEqual(result["code"], 0)

    @patch("vulcanus.restful.response.requests.request")
    def test_get_response_server_error(self, mock_request):
        """Test get_response raises exception on server error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_request.return_value = mock_response
        result = BaseResponse.get_response("GET", TEST_URL)
        self.assertIn("label", result)

    @patch("vulcanus.restful.response.requests.request")
    def test_get_response_non_dict_data(self, mock_request):
        """Test get_response returns PARAM_ERROR for non-dict data."""
        result = BaseResponse.get_response("POST", TEST_URL, data="not_a_dict")
        self.assertEqual(result.get("label"), state.PARAM_ERROR)


class TestBaseResponseVerifyArgs(unittest.TestCase):
    """Tests for BaseResponse.verify_args static method."""

    def test_verify_args_empty_schema(self):
        """Test verify_args with no schema returns SUCCEED."""
        args, status = BaseResponse.verify_args(TEST_DATA, None)
        self.assertEqual(status, state.SUCCEED)


class TestBaseResponseVerifyToken(unittest.TestCase):
    """Tests for BaseResponse.verify_token static method."""

    @patch("vulcanus.restful.response.decode_token")
    @patch("vulcanus.restful.response.RedisProxy")
    def test_verify_token_empty(self, mock_redis, mock_decode):
        """Test verify_token returns TOKEN_ERROR for empty token."""
        result = BaseResponse.verify_token("", {})
        self.assertEqual(result, state.TOKEN_ERROR)

    @patch("vulcanus.restful.response.decode_token")
    @patch("vulcanus.restful.response.RedisProxy")
    def test_verify_token_invalid(self, mock_redis, mock_decode):
        """Test verify_token returns TOKEN_ERROR for invalid token."""
        mock_decode.side_effect = ValueError("invalid")
        result = BaseResponse.verify_token(TEST_TOKEN, {})
        self.assertEqual(result, state.TOKEN_ERROR)


class TestBaseResponseResponse(unittest.TestCase):
    """Tests for BaseResponse.response method."""

    def test_response_success(self):
        """Test response returns JSON with code and data."""
        resource = BaseResponse()
        mock_response = MagicMock()
        mock_response.status_code = 200
        with patch("vulcanus.restful.response.jsonify", return_value=mock_response):
            result = resource.response(state.SUCCEED, data={"info": "ok"})
            self.assertIsNotNone(result)

    def test_response_with_message(self):
        """Test response includes custom message."""
        resource = BaseResponse()
        mock_response = MagicMock()
        with patch("vulcanus.restful.response.jsonify", return_value=mock_response):
            result = resource.response(state.PARAM_ERROR, message="bad param")
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
