#!/usr/bin/python3
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
import ast
import json
import os
import uuid
from functools import wraps
from urllib.parse import unquote

import requests
from flask import g, jsonify, request
from flask_restful import Resource
from jwt.exceptions import ExpiredSignatureError
from retrying import retry
from werkzeug.utils import secure_filename

from vulcanus.conf import configuration
from vulcanus.conf.constant import ADMIN_USER, TIMEOUT, UserRoleType
from vulcanus.database.proxy import MysqlProxy, RedisProxy
from vulcanus.exceptions import DatabaseConnectionFailed
from vulcanus.log.log import LOGGER
from vulcanus.restful.resp import make_response, state
from vulcanus.restful.serialize.validate import validate
from vulcanus.rsa import load_public_key, verify_signature
from vulcanus.token import decode_token, generate_token


class BaseResponse(Resource):
    """
    Restful base class, offer a basic function that can handle the request.
    """

    @classmethod
    def get_response(cls, method, url, data=None, header=None, timeout=TIMEOUT, files=None):
        """
        send a request and get the response

        Args:
            method(str): request method
            url(str): requset url
            data(dict): params in body
            header(dict): request header
            timeout(int): timeout in seconds

        Returns:
            dict: response body
        """

        @retry(
            stop_max_attempt_number=3,
            wait_exponential_multiplier=1000,
            wait_exponential_max=5000,
            retry_on_exception=lambda exception: isinstance(exception, requests.exceptions.RequestException),
        )
        def __http_request(method, url, data, timeout, headers=None, files=None):
            _request_param = dict(method=method, url=url, timeout=timeout, headers=headers)
            if files:
                _request_param.update(dict(data=data, files=files))
            else:
                _request_param.update(dict(json=data))
            response = requests.request(**_request_param)
            if response.status_code in (500, 502, 503, 429, 408):
                raise requests.exceptions.RequestException

            return (
                json.loads(response.text)
                if response.status_code >= 200 and response.status_code < 300
                else make_response(label=state.HTTP_CONNECT_ERROR, message=response.text)
            )

        if data and not isinstance(data, dict):
            LOGGER.error("The param format of rest is not dict")
            return make_response(label=state.PARAM_ERROR)

        try:
            request_body = dict(method=method, url=url, data=data, timeout=timeout, files=files)
            if header:
                request_body.update(dict(headers=header))

            response = __http_request(**request_body)

        except requests.exceptions.RequestException as error:
            LOGGER.error(error)
            response = make_response(label=state.HTTP_CONNECT_ERROR)

        return response

    @classmethod
    def verify_args(cls, args, schema, load=False):
        """
        Verify restful args

        Args:
            args(dict): parameter to be verified
            schema(class): verifier
            load(bool): do parameter deserializing if load is set to true

        Returns:
            Tuple[dict, str]
            a tuple containing two elements (serialized parameter,status code).
        """
        # verify the params
        args, errors = validate(schema, args, load)
        if errors:
            LOGGER.error(errors)
            return args, state.PARAM_ERROR

        return args, state.SUCCEED

    @classmethod
    def verify_token(cls, token, args):
        """
        Verify token

        Args:
            token(str)
            args(dict): request params

        Returns:
            int: status code
        """
        if not token:
            return state.TOKEN_ERROR
        try:
            verify_info = decode_token(token)
        except ExpiredSignatureError:
            return state.TOKEN_EXPIRE
        except ValueError:
            return state.TOKEN_ERROR

        cache_token = RedisProxy.redis_connect.get("token-" + verify_info["sub"] + "-" + verify_info["aud"])
        if not cache_token or cache_token != token:
            return state.TOKEN_ERROR
        g.username = verify_info["sub"]
        return state.SUCCEED

    @staticmethod
    def _set_headers():
        headers = {"Content-Type": "application/json"}
        if "Access-Token" in request.headers:
            headers["Access-Token"] = request.headers["Access-Token"]
        if "X-Cluster-Username" in request.headers:
            headers["X-Cluster-Username"] = request.headers["X-Cluster-Username"]
        g.headers = headers

    @staticmethod
    def _request_body():
        body = dict()
        if request.method != "GET" and not request.files:
            return request.get_json() or dict()

        elif request.files:
            return dict(request.form)

        for key, value in request.args.items():
            if (value.startswith("[") or value.startswith("{")) and (value.endswith("]") or value.endswith("}")):
                body[key] = ast.literal_eval(value)
            elif (value.startswith("%5B") and value.endswith("%5D")) or (
                value.startswith("%7B") and value.endswith("%7D")
            ):
                body[key] = ast.literal_eval(unquote(value))
            else:
                body[key] = value

        return body

    @classmethod
    def verify_request(cls, schema=None, need_token=True, **kwargs):
        """
        Get request args, verify token and parameter

        Args:
            schema (class, optional): parameter verifying schema. Defaults to None.
            need_token (bool, optional): whether need to verify the token. Defaults to True.
            debug (bool, optional): whether need to print args and interface info. Defaults to True.

        Returns:
            dict: request body
            str: verify status code
        """
        request_args = cls._request_body()
        pre_verify_result = state.SUCCEED
        cls._set_headers()
        # distribute service signature
        if all(
            [
                request.headers.get("X-Permission"),
                request.headers.get("X-Signature"),
                request.headers.get("X-Cluster-Username"),
            ]
        ):
            g.username = request.headers.get("X-Cluster-Username")
            from vulcanus.cache import RedisCacheManage

            if RedisProxy.redis_connect.exists("token-" + g.username + "-" + configuration.client_id):
                g.headers["Access-Token"] = RedisProxy.redis_connect.get(
                    "token-" + g.username + "-" + configuration.client_id
                )
            else:
                g.headers["Access-Token"] = generate_token(unique_iden=g.username, aud=configuration.client_id)
                RedisProxy.redis_connect.set(
                    "token-" + g.username + "-" + configuration.client_id, g.headers["Access-Token"]
                )
                RedisProxy.redis_connect.expire("token-" + g.username + "-" + configuration.client_id, 60 * 20)
            cache = RedisCacheManage(domain=configuration.domain, redis_client=RedisProxy.redis_connect)
            signature = request.headers.get("X-Signature")
            if g.username == ADMIN_USER:
                public_key = cache.location_cluster["public_key"]
            else:
                clusters = cache.get_user_cluster_private_key
                sub_cluster_user = clusters.get(cache.location_cluster["cluster_id"])
                public_key = sub_cluster_user["public_key"] if sub_cluster_user else None

            if not public_key or not verify_signature(request_args, signature, load_public_key(public_key)):
                return request_args, state.PERMESSION_ERROR
            need_token = False
        if schema:
            request_args, pre_verify_result = cls.verify_args(request_args, schema, True)
            if pre_verify_result != state.SUCCEED:
                return request_args, pre_verify_result
        if need_token:
            pre_verify_result = cls.verify_token(request.headers.get("Access-Token"), request_args)

        return request_args, pre_verify_result

    @classmethod
    def verify_upload_request(cls, save_path, file_key="file"):
        """
        verify upload request's token, save file into save_path/username
        Args:
            save_path (str): path the file to be saved
            file_key (str): body key for the file

        Returns:
            int: verify status code
            str: user name
            str: file's name
        """
        args = request.get_json()
        LOGGER.debug(request.base_url)
        LOGGER.debug("Interface %s received args: %s", request.endpoint, args)

        access_token = request.headers.get("access-token")
        if args is None:
            args = {}
        verify_res = cls.verify_token(access_token, args)

        file_name = ""
        username = ""
        if verify_res == state.SUCCEED:
            file = request.files.get(file_key)
            if file is None or not file.filename:
                return state.PARAM_ERROR, "", file_name

            username = g.username
            filename = secure_filename(file.filename)
            file_name = str(uuid.uuid4()) + "." + filename.rsplit('.', 1)[-1]

            if not os.path.exists(os.path.join(save_path, username)):
                os.makedirs(os.path.join(save_path, username))

            file.save(os.path.join(save_path, username, file_name))
        return verify_res, username, file_name

    def response(self, code, message=None, data=None):
        """
        Gets the api response body information

        Args:
            code: status code of the response
            message: customize the prompt information
            data: response body content

        Returns:
            dict: response body e.g
                {
                    "code":"",
                    "message":"",
                    "data": dict/str/list
                    "label": ""
                }
        """
        return jsonify(make_response(label=code, message=message, data=data))

    @staticmethod
    def handle(schema=None, token=True, debug=False, proxy=None):
        def verify_handle(api_view):
            @wraps(api_view)
            def wrapper(self, **kwargs):
                params, status = BaseResponse.verify_request(schema, need_token=token, debug=debug)
                if status != state.SUCCEED:
                    return self.response(code=status)

                params.update(kwargs)
                if not proxy:
                    return api_view(self, **params)
                try:
                    if not issubclass(proxy, MysqlProxy):
                        db_proxy = proxy()
                        return api_view(self, callback=db_proxy, **params)
                    with proxy() as db_proxy:
                        return api_view(self, callback=db_proxy, **params)
                except DatabaseConnectionFailed:
                    return self.response(code=state.DATABASE_CONNECT_ERROR)

            return wrapper

        return verify_handle

    @staticmethod
    def permession():
        def verify_permession(api_view):
            @wraps(api_view)
            def wrapper(self, host_id, *args, **kwargs):
                from vulcanus.cache import RedisCacheManage

                cache = RedisCacheManage(domain=configuration.domain, redis_client=RedisProxy.redis_connect)
                if cache.user_role == UserRoleType.ADMINISTRATOR:
                    return api_view(self, host_id=host_id, *args, **kwargs)

                if not host_id:
                    return api_view(self, host_id=host_id, *args, **kwargs)

                if not cache.get_user_group_hosts():
                    return self.response(code=state.PERMESSION_ERROR)

                host_ids = [host_in for host_ids in cache.all_groups_hosts.values() for host_in in host_ids]
                if host_id not in host_ids:
                    return self.response(code=state.PERMESSION_ERROR)

                return api_view(self, host_id=host_id, *args, **kwargs)

            return wrapper

        return verify_permession
