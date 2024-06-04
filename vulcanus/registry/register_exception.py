#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2024. All rights reserved.
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
Description: Self-defined Exception class for register center
"""


class RegisterCenterError(Exception):
    """Base exception class for register center related exceptions."""

    pass


class ConfigurationError(RegisterCenterError):
    """Raised when there is an error in the configuration of the register center."""

    pass


class ConnectionError(RegisterCenterError):
    """Exception raised when there is a connection error with the register center."""

    pass


class DisconnectionError(RegisterCenterError):
    """Exception raised when there is a connection error with the register center."""

    pass


class RegistrationError(RegisterCenterError):
    """Exception raised when there is an error during service registration."""

    pass


class DiscoveryError(RegisterCenterError):
    """Exception raised when there is an error during service discovery."""

    pass


class NodeNotFoundError(RegisterCenterError):
    """Exception raised when a register center node is not found."""

    pass


class InvalidDataError(RegisterCenterError):
    """Exception raised when the data in the register center is invalid."""

    pass


class NodeDeletionError(Exception):
    """Raised when an error occurs during node deletion in the register center."""

    pass
