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
from datetime import datetime, timedelta
import time
import jwt
from jwt.exceptions import ExpiredSignatureError
from vulcanus.conf.constant import PRIVATE_KEY


__all__ = ["generate_token", "decode_token", "get_timedelta"]


def get_timedelta(minutes: int = 20) -> int:
    """
    Gets the time increment after the specified minute

    Args:
        minutes: Specified number of minutes

    Returns:
        Time increment value
    """
    date_span = datetime.now()
    if minutes:
        date_span = date_span + timedelta(minutes=minutes)

    time_span = time.strptime(
        date_span.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"
    )
    return int(time.mktime(time_span))


def generate_token(unique_iden, minutes=20, **kwargs):
    """
    Generates token values based on jwt validation

    Args:
        unique_iden: unique Id of a user can be an ID, user name, mobile phone number, or email address

    Returns:
        token: (str) generated token value
    """
    if not unique_iden:
        return ValueError("A unique identifier is missing")
    token_body = {
        "iat": int(time.time()),
        "exp": get_timedelta(20),
    }
    if minutes and minutes != 20:
        token_body["exp"] = get_timedelta(minutes)
    token_body.update(kwargs)
    try:
        token_body["key"] = unique_iden
        token_body["create_time"] = time.localtime()
        return jwt.encode(
            token_body,
            PRIVATE_KEY,
            algorithm="HS256",
            headers=dict(alg="HS256"),
        )
    except Exception:
        raise ValueError("Token generation failed")


def decode_token(token):
    """
    Resolves the token to be authenticated

    Args:
        token: The token to be resolved

    Return:
        contents of the parsed token
        A data exception error is thrown when the token content is invalid
    """
    if not token:
        raise ValueError("Please enter a valid token")
    try:
        return jwt.decode(token, PRIVATE_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise ExpiredSignatureError("Signature has expired")
    except Exception:
        raise ValueError("It is not a valid token")
