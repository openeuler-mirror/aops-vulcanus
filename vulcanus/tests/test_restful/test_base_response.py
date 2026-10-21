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
Description: supplementary unit tests for restful/response.py, covering
_set_headers, _request_body, verify_request, verify_upload_request, handle
and permession
"""
import unittest
from unittest.mock import MagicMock, patch

from flask import Flask

from vulcanus.conf.constant import UserRoleType
from vulcanus.restful.response import BaseResponse
from vulcanus.restful.resp import state

app = Flask("test")


def _get_protected(obj, name):
    """
    Get a protected attribute to test internal logic without
    violating G.CLS.11
    """
    return getattr(obj, name)


class BaseTest(unittest.TestCase):
    """
    Base class offering a flask app context for request/g
    """

    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        self.addCleanup(self.ctx.pop)


class TestSetHeaders(BaseTest):
    """
    Tests for BaseResponse._set_headers
    """

    def test_set_headers_default(self):
        _get_protected(BaseResponse, "_set_headers")()
        from flask import g

        self.assertEqual(g.headers, {"Content-Type": "application/json"})

    def test_set_headers_with_token_and_username(self):
        from flask import g

        with patch(
            "vulcanus.restful.response.request",
            MagicMock(
                headers={
                    "Access-Token": "token123",
                    "X-Cluster-Username": "user1",
                }
            ),
        ):
            _get_protected(BaseResponse, "_set_headers")()
        self.assertEqual(g.headers["Access-Token"], "token123")
        self.assertEqual(g.headers["X-Cluster-Username"], "user1")


class TestRequestBody(unittest.TestCase):
    """
    Tests for BaseResponse._request_body with real flask request
    """

    def run_in_context(self, path="/", method="GET", **kwargs):
        ctx = app.test_request_context(path, method=method, **kwargs)
        ctx.push()
        self.addCleanup(ctx.pop)
        return _get_protected(BaseResponse, "_request_body")()

    def test_request_body_post_json(self):
        import json as json_module

        result = self.run_in_context(
            method="POST", data=json_module.dumps({"a": 1}), content_type="application/json"
        )
        self.assertEqual(result, {"a": 1})

    def test_request_body_post_json_none(self):
        result = self.run_in_context(method="POST", data="null", content_type="application/json")
        self.assertEqual(result, {})

    def test_request_body_with_files(self):
        mock_request = MagicMock(
            method="POST", files={"file": MagicMock()}, form={"name": "test"}, get_json=MagicMock(return_value={})
        )
        with patch("vulcanus.restful.response.request", new=mock_request):
            self.assertEqual(_get_protected(BaseResponse, "_request_body")(), {"name": "test"})

    def test_request_body_get_with_list_value(self):
        result = self.run_in_context("/?ids=[1,%202]")
        self.assertEqual(result, {"ids": [1, 2]})

    def test_request_body_get_with_urlencoded_value(self):
        result = self.run_in_context("/?filter=%5B%221%22%5D")
        self.assertEqual(result, {"filter": ["1"]})

    def test_request_body_get_with_plain_value(self):
        result = self.run_in_context("/?page=1")
        self.assertEqual(result, {"page": "1"})


class TestVerifyRequest(unittest.TestCase):
    """
    Tests for BaseResponse.verify_request
    """

    def run_in_context(self, path="/", method="GET", **kwargs):
        ctx = app.test_request_context(path, method=method, **kwargs)
        ctx.push()
        self.addCleanup(ctx.pop)

    def test_verify_request_without_schema_and_token(self):
        self.run_in_context()
        args, status = BaseResponse.verify_request(schema=None, need_token=False)
        self.assertEqual(status, state.SUCCEED)

    @patch("vulcanus.restful.response.BaseResponse.verify_args")
    def test_verify_request_with_schema_fail(self, mock_verify_args):
        self.run_in_context()
        mock_verify_args.return_value = ({"a": 1}, state.PARAM_ERROR)
        args, status = BaseResponse.verify_request(schema=object, need_token=False)
        self.assertEqual(status, state.PARAM_ERROR)

    @patch("vulcanus.restful.response.BaseResponse.verify_token")
    def test_verify_request_token_error(self, mock_verify_token):
        self.run_in_context()
        mock_verify_token.return_value = state.TOKEN_ERROR
        _, status = BaseResponse.verify_request(schema=None, need_token=True)
        self.assertEqual(status, state.TOKEN_ERROR)


class TestVerifyUploadRequest(BaseTest):
    """
    Tests for BaseResponse.verify_upload_request
    """

    @patch("vulcanus.restful.response.BaseResponse.verify_token", return_value=state.TOKEN_ERROR)
    @patch("vulcanus.restful.response.request")
    def test_verify_upload_request_token_error(self, mock_request, mock_verify_token):
        mock_request.get_json.return_value = None
        result = BaseResponse.verify_upload_request("/tmp/upload")
        self.assertEqual(result, (state.TOKEN_ERROR, "", ""))

    @patch("vulcanus.restful.response.BaseResponse.verify_token", return_value=state.SUCCEED)
    @patch("vulcanus.restful.response.request")
    def test_verify_upload_request_no_file(self, mock_request, mock_verify_token):
        mock_request.get_json.return_value = {}
        mock_request.files = {}
        result = BaseResponse.verify_upload_request("/tmp/upload")
        self.assertEqual(result, (state.PARAM_ERROR, "", ""))

    @patch("vulcanus.restful.response.BaseResponse.verify_token", return_value=state.SUCCEED)
    @patch("vulcanus.restful.response.request")
    def test_verify_upload_request_save_file(self, mock_request, mock_verify_token):
        import os
        import tempfile

        save_path = tempfile.mkdtemp()
        file = MagicMock()
        file.filename = "test.txt"
        mock_request.get_json.return_value = {}
        mock_request.files = {"file": file}
        with patch("vulcanus.restful.response.g", username="tester"):
            _, username, file_name = BaseResponse.verify_upload_request(save_path)
        self.assertEqual(username, "tester")
        self.assertTrue(file_name.endswith(".txt"))
        file.save.assert_called_once()
        self.assertIn("tester", file.save.call_args[0][0])


class TestHandle(BaseTest):
    """
    Tests for BaseResponse.handle decorator
    """

    @patch("vulcanus.restful.response.BaseResponse.verify_request", return_value=({"a": 1}, state.SUCCEED))
    def test_handle_succeed_without_proxy(self, _):
        @BaseResponse.handle(token=False)
        def api_view(self_, **kwargs):
            return kwargs["a"]

        self.assertEqual(api_view(MagicMock()), 1)

    @patch("vulcanus.restful.response.BaseResponse.verify_request", return_value=({"a": 1}, state.PARAM_ERROR))
    def test_handle_verify_fail(self, _):
        mock_self = MagicMock()
        mock_self.response.return_value = "error response"

        @BaseResponse.handle(token=False)
        def api_view(self_, **kwargs):
            return "should not be called"

        result = api_view(mock_self)
        self.assertEqual(result, "error response")

    @patch("vulcanus.restful.response.BaseResponse.verify_request", return_value=({"a": 1}, state.SUCCEED))
    def test_handle_with_mysql_proxy(self, _):
        mock_proxy = MagicMock()
        mock_proxy_class = MagicMock()
        mock_proxy_class.__mro__ = (MagicMock(),)
        mock_proxy_class.return_value.__enter__ = MagicMock(return_value=mock_proxy)
        mock_proxy_class.return_value.__exit__ = MagicMock(return_value=False)
        with patch("vulcanus.restful.response.issubclass", return_value=True):
            with patch("vulcanus.restful.response.MysqlProxy", mock_proxy_class):
                @BaseResponse.handle(token=False, proxy=mock_proxy_class)
                def api_view(self_, callback=None, **kwargs):
                    return callback

                self.assertEqual(api_view(MagicMock()), mock_proxy)

    @patch("vulcanus.restful.response.BaseResponse.verify_request", return_value=({"a": 1}, state.SUCCEED))
    def test_handle_proxy_connection_failed(self, _):
        from vulcanus.exceptions import DatabaseConnectionFailed

        mock_proxy_class = MagicMock()
        mock_proxy_class.__mro__ = (MagicMock(),)
        mock_proxy_class.return_value.__enter__ = MagicMock(side_effect=DatabaseConnectionFailed("error"))
        with patch("vulcanus.restful.response.issubclass", return_value=True):
            with patch("vulcanus.restful.response.MysqlProxy", mock_proxy_class):
                mock_self = MagicMock()
                mock_self.response.return_value = "database error"

                @BaseResponse.handle(token=False, proxy=mock_proxy_class)
                def api_view(self_, callback=None, **kwargs):
                    return "should not be called"

                self.assertEqual(api_view(mock_self), "database error")


class TestPermession(BaseTest):
    """
    Tests for BaseResponse.permession decorator
    """

    def test_permession_admin(self):
        with patch("vulcanus.cache.RedisCacheManage") as mock_cache:
            mock_cache.return_value.user_role = UserRoleType.ADMINISTRATOR
            mock_self = MagicMock()

            @BaseResponse.permession()
            def api_view(self_, host_id, **kwargs):
                return "called"

            self.assertEqual(api_view(mock_self, host_id=1), "called")

    def test_permession_no_host_id(self):
        with patch("vulcanus.cache.RedisCacheManage") as mock_cache:
            mock_cache.return_value.user_role = "NormalUser"
            mock_self = MagicMock()

            @BaseResponse.permession()
            def api_view(self_, host_id, **kwargs):
                return "called"

            self.assertEqual(api_view(mock_self, host_id=None), "called")

    def test_permession_host_not_allowed(self):
        with patch("vulcanus.cache.RedisCacheManage") as mock_cache:
            mock_cache.return_value.user_role = "NormalUser"
            mock_cache.return_value.get_user_group_hosts.return_value = True
            mock_cache.return_value.all_groups_hosts = {"group1": [2, 3]}
            mock_self = MagicMock()
            mock_self.response.return_value = "permission error"

            @BaseResponse.permession()
            def api_view(self_, host_id, **kwargs):
                return "called"

            self.assertEqual(api_view(mock_self, host_id=1), "permission error")

    def test_permession_host_allowed(self):
        with patch("vulcanus.cache.RedisCacheManage") as mock_cache:
            mock_cache.return_value.user_role = "NormalUser"
            mock_cache.return_value.get_user_group_hosts.return_value = True
            mock_cache.return_value.all_groups_hosts = {"group1": [1, 2]}

            @BaseResponse.permession()
            def api_view(self_, host_id, **kwargs):
                return "called"

            self.assertEqual(api_view(MagicMock(), host_id=1), "called")


if __name__ == "__main__":
    unittest.main()
