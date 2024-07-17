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
import json
import uuid
from random import choice
from typing import List, Optional

from kazoo.client import KazooClient
from kazoo.exceptions import KazooException, NodeExistsError
from kazoo.protocol.states import KazooState, ZnodeStat

from vulcanus.log.log import LOGGER
from vulcanus.registry.register_exception import ConnectionError, DisconnectionError
from vulcanus.registry.register_service import RegisterCenter


class ZookeeperRegisterCenter(RegisterCenter):
    """
    Implementation of a ZooKeeper-based register center.
    """

    def __init__(self, hosts: str):
        super().__init__(hosts)
        self.zk = KazooClient(hosts)
        self._service_path = None

    @property
    def path(self) -> str:
        return self._service_path

    def connection_listener(self, state: str) -> None:
        """
        Listener for ZooKeeper connection state changes.

        Args:
            state (KazooState): The new connection state.
        """
        if state == KazooState.CONNECTED:
            LOGGER.info("zookeeper connected")
        elif state == KazooState.LOST:
            LOGGER.error("zookeeper connect lost!")
        else:
            LOGGER.error("zookeeper disconnected")

    @property
    def connected(self) -> bool:
        return self.zk.connected

    def connect(self) -> None:
        """
        Connect to the ZooKeeper server.
        """
        try:
            self.zk.start()
            self.zk.add_listener(self.connection_listener)
        except KazooException as error:
            LOGGER.error("Failed to connect to Zookeeper")
            raise ConnectionError(f"Failed to connect to Zookeeper") from error

    def disconnect(self) -> None:
        """
        Disconnect from the ZooKeeper server.
        """
        try:
            self.zk.stop()
        except KazooException as error:
            LOGGER.error("Failed to disconnect to Zookeeper")
            raise DisconnectionError(f"Failed to disconnect to Zookeeper") from error

    def register_service(self, service_name: str, service_info: dict, ephemeral: bool = False) -> bool:
        """
        Register a service in ZooKeeper.

        Args:
            service_name (str): The name of the service, which differentiates it from other microservices
            service_info (dict): Information about the service node, e.g., {"address": "localhost", "port": 5000}.
            ephemeral (bool): Whether the registered node is ephemeral. False indicates a persistent node.
        Returns:
            bool: Registration status.
        """
        self._service_path = f'/services/{service_name}'
        self.zk.ensure_path(self._service_path)
        service_node = f"{self._service_path}/{uuid.uuid4()}"
        try:
            register_result = self.zk.create(
                path=service_node, value=json.dumps(service_info).encode("utf-8"), ephemeral=ephemeral
            )
        except NodeExistsError:
            return False

        return register_result == service_node

    def exists(self, service_path:str) -> Optional[ZnodeStat]:
        """
        Check if a service path exists in ZooKeeper.

        Args:
            service_path (str): The path of the service node.

        Returns:
            Optional[ZnodeStat]: The ZnodeStat object if the node exists, None otherwise.
        """
        return self.zk.exists(service_path)

    def get_children(self, service_path: str) -> List[str]:
        """
        Get the children nodes under a given service path.

        Args:
            service_path (str): The path of the service node.

        Returns:
            list: List of child nodes.
        """
        if not self.exists(service_path):
            LOGGER.error("please check whether the service exists")
            return []

        children = self.zk.get_children(service_path)
        if not children:
            return []

        return children

    def get_all_service_instance(self, service_name: str) -> List[dict]:
        """
        Get all instances of a service.

        Args:
            service_name (str): The name of the service.

        Returns:
            list: List of service instance information.
        """
        services = []
        service_path = f'/services/{service_name}'
        children = self.get_children(service_path)

        for child in children:
            data, _ = self.zk.get("/%s/%s" % (service_path, child))
            services.append(json.loads(data.decode('utf-8')))

        return services

    def get_service(self, service_name: str) -> Optional[dict]:
        """
        Get a random instance of a service.

        Args:
            service_name (str): The name of the service.

        Returns:
            Optional[dict]: Service instance information.
        """
        service_path = f'/services/{service_name}'
        children = self.get_children(service_path)
        if not children:
            return None

        child = choice(children)
        data, _ = self.zk.get("/%s/%s" % (service_path, child))
        service = json.loads(data.decode('utf-8'))

        return service

    def delete_service(self, service_name: str, recursive: bool = True) -> bool:
        """
        Delete a service and its instances.

        Args:
            service_name (str): The name of the service.
            recursive (bool): Whether to delete the service recursively. Defaults to True.
        """
        instance_path = f'/services/{service_name}'
        if not self.zk.exists(instance_path):
            return True
        try:
            self.zk.delete(path=instance_path, recursive=recursive)
            return True
        except KazooException as error:
            LOGGER.error(f"Failed to delete service node from zookeeper, {error}")
            return False
