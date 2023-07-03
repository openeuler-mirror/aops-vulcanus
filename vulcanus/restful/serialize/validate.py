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
Description:
"""
import re

from marshmallow import Schema, ValidationError, fields


def validate(verifier, data, load=False):
    """
    Validation method

    Args:
        verifier(class): the class of the validator
        data(dict): parameter to be verified
        load(bool): do parameter deserializing if load is set to true

    Returns:
        dict: verified parameter
        dict: messages when verified failed
    """
    result = data
    errors = dict()
    if load:
        try:
            result = verifier().load(data)
        except ValidationError as err:
            errors = err.messages
    else:
        errors = verifier().validate(data)

    return result, errors


class ValidateRules:
    """
    Custom validation rules
    """

    @staticmethod
    def space_character_check(string: str) -> None:
        """
        one of validation rules for string, no spaces are allowed at the beginning or end.
        """
        if len(string.strip()) != len(string):
            raise ValidationError("there may be space character exists at the beginning or end!")

    @staticmethod
    def account_name_check(string: str) -> None:
        """
        validation rules for username, which only contains string or number
        """
        if not re.findall("[a-zA-Z0-9]{5,20}", string):
            raise ValidationError("username should only contains string or number, between 5 and 20 characters!")

    @staticmethod
    def account_password_check(string: str) -> None:
        """
        validation rules for password, which only contains string or number
        """
        if not re.findall("[a-zA-Z0-9]{6,20}", string):
            raise ValidationError("password should only contains string or number, between 6 and 20 characters!!")


class PaginationSchema(Schema):
    """
    filter schema of paging parameter
    """

    page = fields.Integer(required=False, validate=lambda s: 10**6 > s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 10**3 > s > 0)
