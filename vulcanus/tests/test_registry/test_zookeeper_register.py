# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2024. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Description: unit tests for registry/register_service/zookeeper.py
"""
import json
import os
import unittest
from unittest.mock import patch, MagicMock

from vulcanus.registry.register_service.zookeeper import ZookeeperRegisterCenter

HOSTS = "127.0.0.1:2181"
SERVICE_NAME = "test_service"
SERVICE_INFO = {"address": "127.0.0.1", "port": 8080}
NODE_ID = "test-uuid"


class TestZookeeperRegisterCenterInit(unittest.TestCase):
    """Tests for ZookeeperRegisterCenter initialization."""

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_init(self, mock_kazoo):
        """Test ZookeeperRegisterCenter initializes with hosts."""
        center = ZookeeperRegisterCenter(HOSTS)
        self.assertIsNotNone(center.zk)


class TestZookeeperRegisterCenterConnect(unittest.TestCase):
    """Tests for ZookeeperRegisterCenter connect/disconnect."""

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_connect_success(self, mock_kazoo):
        """Test connect starts the client."""
        mock_client = MagicMock()
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        center.connect()
        mock_client.start.assert_called_once()

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_disconnect_success(self, mock_kazoo):
        """Test disconnect stops the client."""
        mock_client = MagicMock()
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        center.disconnect()
        mock_client.stop.assert_called_once()

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_connected_property(self, mock_kazoo):
        """Test connected property returns client state."""
        mock_client = MagicMock()
        mock_client.connected = True
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        self.assertTrue(center.connected)


class TestZookeeperRegisterCenterRegisterService(unittest.TestCase):
    """Tests for ZookeeperRegisterCenter.register_service method."""

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_register_success(self, mock_kazoo):
        """Test register_service returns True on success."""
        mock_client = MagicMock()
        mock_client.create.return_value = os.path.join("/services", SERVICE_NAME, NODE_ID)
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        result = center.register_service(SERVICE_NAME, SERVICE_INFO)
        self.assertTrue(result)

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_register_node_exists(self, mock_kazoo):
        """Test register_service returns False when node exists."""
        from kazoo.exceptions import NodeExistsError
        mock_client = MagicMock()
        mock_client.create.side_effect = NodeExistsError()
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        result = center.register_service(SERVICE_NAME, SERVICE_INFO)
        self.assertFalse(result)


class TestZookeeperRegisterCenterGetService(unittest.TestCase):
    """Tests for ZookeeperRegisterCenter.get_service method."""

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_get_service_found(self, mock_kazoo):
        """Test get_service returns service info when found."""
        mock_client = MagicMock()
        mock_client.exists.return_value = True
        mock_client.get_children.return_value = [NODE_ID]
        mock_client.get.return_value = (json.dumps(SERVICE_INFO).encode("utf-8"), None)
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        result = center.get_service(SERVICE_NAME)
        self.assertEqual(result["address"], SERVICE_INFO["address"])

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_get_service_not_found(self, mock_kazoo):
        """Test get_service returns None when not found."""
        mock_client = MagicMock()
        mock_client.exists.return_value = None
        mock_client.get_children.return_value = []
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        result = center.get_service(SERVICE_NAME)
        self.assertIsNone(result)


class TestZookeeperRegisterCenterDeleteService(unittest.TestCase):
    """Tests for ZookeeperRegisterCenter.delete_service method."""

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_delete_service_exists(self, mock_kazoo):
        """Test delete_service returns True when deleted."""
        mock_client = MagicMock()
        mock_client.exists.return_value = True
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        result = center.delete_service(SERVICE_NAME)
        self.assertTrue(result)
        mock_client.delete.assert_called_once()

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_delete_service_not_exists(self, mock_kazoo):
        """Test delete_service returns True for non-existent service."""
        mock_client = MagicMock()
        mock_client.exists.return_value = None
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        result = center.delete_service(SERVICE_NAME)
        self.assertTrue(result)


class TestZookeeperRegisterCenterGetChildren(unittest.TestCase):
    """Tests for ZookeeperRegisterCenter.get_children method."""

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_get_children_exists(self, mock_kazoo):
        """Test get_children returns children list."""
        mock_client = MagicMock()
        mock_client.exists.return_value = True
        mock_client.get_children.return_value = ["child1", "child2"]
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        result = center.get_children("/services/test")
        self.assertEqual(result, ["child1", "child2"])

    @patch("vulcanus.registry.register_service.zookeeper.KazooClient")
    def test_get_children_not_exists(self, mock_kazoo):
        """Test get_children returns empty list."""
        mock_client = MagicMock()
        mock_client.exists.return_value = None
        mock_kazoo.return_value = mock_client
        center = ZookeeperRegisterCenter(HOSTS)
        result = center.get_children("/services/test")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
