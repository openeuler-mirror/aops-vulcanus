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
"""
Time:
Author:
Description: response function
"""
from flask import g
import os
import json
from functools import wraps
import uuid
import requests
from jwt.exceptions import ExpiredSignatureError
from flask import request, jsonify
from flask_restful import Resource
from werkzeug.utils import secure_filename
from vulcanus.database.proxy import DataBaseProxy, RedisProxy
from vulcanus.log.log import LOGGER
from vulcanus.restful.serialize.validate import validate
from vulcanus.restful.resp import make_response, state
from vulcanus.token import decode_token
from vulcanus.conf import configuration


class BaseResponse(Resource):
    """
    Restful base class, offer a basic function that can handle the request.
    """
    @classmethod
    def get_response(cls, method, url, data, header=None, timeout=600):
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
        if not isinstance(data, dict):
            LOGGER.error("The param format of rest is not dict")
            result = make_response(label=state.PARAM_ERROR)
            return result

        try:
            if header:
                response = requests.request(
                    method=method, url=url, json=data, headers=header, timeout=timeout)
            else:
                response = requests.request(
                    method=method, url=url, json=data, timeout=timeout)
            if response.status_code != 200:
                result = make_response(label=state.SERVER_ERROR)
            else:
                result = json.loads(response.text)
        except requests.exceptions.RequestException as error:
            LOGGER.error(error)
            result = make_response(label=state.HTTP_CONNECT_ERROR)

        return result

    @classmethod
    def get_result(cls, res, method, url, args):
        """
        Get response result

        Args:
            res(int): verify result
            method(str): restful function
            url(str): restful url
            args(dict): parameter

        Returns:
            dict: response body
        """
        if res == state.SUCCEED:
            response = cls.get_response(method, url, args)
        else:
            response = make_response(res)

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
            int: status code
        """
        # verify the params
        args, errors = validate(schema, args, load)
        if errors:
            LOGGER.error(errors)
            return state.PARAM_ERROR

        return state.SUCCEED

    @classmethod
    def verify_token(cls, token, args):
        """
        Verify token

        Args:
            token(str)
            args(dict)

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

        cache_token = RedisProxy.redis_connect.get(
            "token_" + verify_info["key"])
        if not cache_token:
            return state.TOKEN_ERROR

        args['username'] = verify_info["key"]
        return state.SUCCEED

    @classmethod
    def verify_request(cls, schema=None, need_token=True, debug=True):
        """
        Get request args, verify token and parameter

        Args:
            schema (class, optional): parameter verifying schema. Defaults to None.
            need_token (bool, optional): whether need to verify the token. Defaults to True.
            debug (bool, optional): whether need to print args and interface info. Defaults to True.

        Returns:
            dict: request args
            int: verify status code
        """
        args = request.args.to_dict() if request.method == "GET" else request.get_json() or dict()

        if debug:
            LOGGER.debug(request.base_url)
            LOGGER.debug("Interface %s received args: %s",
                         request.endpoint, args)

        access_token = request.headers.get('access_token')
        verify_res = state.SUCCEED
        if schema:
            verify_res = cls.verify_args(args, schema)
            if verify_res != state.SUCCEED:
                return args, verify_res
        exempt_authentication = request.headers.get('exempt_authentication')
        if exempt_authentication:
            status = state.SUCCEED if exempt_authentication == configuration.individuation.get(
                "EXEMPT_AUTHENTICATION") else state.TOKEN_ERROR
            args["username"] = request.headers.get('local_account')
            args["timed"] = True
            return args, status

        if need_token:
            verify_res = cls.verify_token(access_token, args)

        return args, verify_res

    @classmethod
    def verify_upload_request(cls, save_path, file_key='file'):
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

        access_token = request.headers.get('access_token')
        if args is None:
            args = {}
        verify_res = cls.verify_token(access_token, args)

        file_name = ""
        username = ""
        if verify_res == state.SUCCEED:
            file = request.files.get(file_key)
            if file is None or not file.filename:
                return state.PARAM_ERROR, "", file_name

            username = args["username"]
            filename = secure_filename(file.filename)
            file_name = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[-1]

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
    def handle(schema=None, token=True, debug=False, proxy: DataBaseProxy = None, session=None):
        def verify_handle(api_view):
            @wraps(api_view)
            def wrapper(self, **kwargs):
                params, status = self.verify_request(
                    schema, need_token=token, debug=debug)
                if status != state.SUCCEED:
                    return self.response(code=status)

                params.update(kwargs)
                _session = session if session else g.session
                if proxy and not proxy.connect(session=_session):
                    return self.response(code=state.DATABASE_CONNECT_ERROR)

                return api_view(self, callback=proxy, **params) if proxy else api_view(self, **params)

            return wrapper
        return verify_handle
