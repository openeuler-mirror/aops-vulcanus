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
from typing import Any, Optional

from vulcanus.registry.register_exception import ConfigurationError
from vulcanus.registry.register_exception import NodeNotFoundError
from vulcanus.registry.register_service import RegisterCenter
from vulcanus.registry.register_service.zookeeper import ZookeeperRegisterCenter


class Service:
    def __init__(self, hosts, center_type: str = RegisterCenter.CONFIG):
        """
        Initialize the Service object.

        Args:
            hosts (str): host addresses for the register center. e.g 127.0.0.1:2181
            center_type (str, optional): The type of register center. Defaults to RegisterCenter.CONFIG.
        """
        if center_type not in RegisterCenter.meta:
            raise ConfigurationError("Unsupported register center type")
        self._hosts = hosts
        self._center = self._init(center_type)

    def _init(self, center_type: str) -> Optional[Any]:
        """
        Initialize and return the specific register center object based on the center_type.

        Args:
            center_type (str): The type of register center.

        Returns:
            Optional[Any]: The initialized register center object.
        """
        if center_type == RegisterCenter.ZOOKEEPER:
            center = ZookeeperRegisterCenter(self._hosts)
            return center

        return None

    def connect(self) -> None:
        """
        Connect to the register center.
        """
        self._center.connect()

    def exists(self, service: str) -> Optional[Any]:
        """
        Check if the given service exists in the register center.

        Args:
            service (str): The name of the service.

        Returns:
            Optional[Any]: The nodeStat object if the node exists, None otherwise.
        """
        return self._center.exists(service)

    def disconnect(self) -> None:
        """
        Disconnect from the register center.
        """
        self._center.disconnect()

    def register_service(self, service_name, service_info: dict) -> bool:
        """
        Register a service in the register center.

        Args:
            service_name (str): The name of the service.
            service_info (dict): The information of the service.

        Returns:
            bool: The result of the registration process.
        """
        if not self._center.connected:
            self.connect()
        register = self._center.register_service(service_name, service_info)
        return register

    def get_service(self, service_name: str, schema: str = "http") -> str:
        """
        Get the address of a service from the register center.

        Args:
            service_name (str): The name of the service.
            schema (str, optional): The schema to use for the service address. Defaults to "http".

        Returns:
            str: The address of the service.

        Raises:
            NodeNotFoundError: If the service is not found in the register center.
        """
        if not self._center.connected:
            self.connect()
        services = self._center.get_service(service_name)
        if services is None:
            raise NodeNotFoundError("Service not found")
        if schema == "http":
            return f"{schema}://{services['address']}:{services['port']}"

    def delete_service(self, service_name: str, recursive: bool = True) -> None:
        """
        Delete a service from the register center.

        Args:
            service_name (str): The name of the service.
            recursive (bool): Whether to delete the service recursively. Defaults to True.
        """
        if not self._center.connected:
            self.connect()
        self._center.delete_service(service_name, recursive)
