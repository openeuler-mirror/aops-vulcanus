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
Description: unit tests for registry/register_center.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vulcanus.registry.register_center import Service
from vulcanus.registry.register_exception import ConfigurationError, NodeNotFoundError
from vulcanus.registry.register_service import RegisterCenter

HOSTS = "127.0.0.1:2181"
SERVICE_NAME = "test_service"
SERVICE_INFO = {"address": "127.0.0.1", "port": 8080}


class TestServiceInit(unittest.TestCase):
    """Tests for Service initialization."""

    @patch("vulcanus.registry.register_center.ZookeeperRegisterCenter")
    def test_init_valid_type(self, mock_zk):
        """Test Service init with valid center type."""
        mock_center = MagicMock()
        mock_zk.return_value = mock_center
        service = Service(HOSTS, RegisterCenter.ZOOKEEPER)
        self.assertIsNotNone(service._center)

    def test_init_invalid_type(self):
        """Test Service init with invalid center type raises ConfigurationError."""
        with self.assertRaises(ConfigurationError):
            Service(HOSTS, "invalid_type")


class TestServiceGetService(unittest.TestCase):
    """Tests for Service.get_service method."""

    @patch("vulcanus.registry.register_center.ZookeeperRegisterCenter")
    def test_get_service_found(self, mock_zk):
        """Test get_service returns address when service found."""
        mock_center = MagicMock()
        mock_center.connected = False
        mock_center.get_service.return_value = SERVICE_INFO
        mock_zk.return_value = mock_center
        service = Service(HOSTS, RegisterCenter.ZOOKEEPER)
        result = service.get_service(SERVICE_NAME)
        self.assertIn("http", result)
        self.assertIn("8080", result)

    @patch("vulcanus.registry.register_center.ZookeeperRegisterCenter")
    def test_get_service_not_found(self, mock_zk):
        """Test get_service raises NodeNotFoundError when not found."""
        mock_center = MagicMock()
        mock_center.connected = False
        mock_center.get_service.return_value = None
        mock_zk.return_value = mock_center
        service = Service(HOSTS, RegisterCenter.ZOOKEEPER)
        with self.assertRaises(NodeNotFoundError):
            service.get_service(SERVICE_NAME)

    @patch("vulcanus.registry.register_center.ZookeeperRegisterCenter")
    def test_get_service_https(self, mock_zk):
        """Test get_service with https schema."""
        mock_center = MagicMock()
        mock_center.connected = True
        mock_center.get_service.return_value = SERVICE_INFO
        mock_zk.return_value = mock_center
        service = Service(HOSTS, RegisterCenter.ZOOKEEPER)
        result = service.get_service(SERVICE_NAME, schema="https")
        self.assertIn("https", result)


class TestServiceRegisterService(unittest.TestCase):
    """Tests for Service.register_service method."""

    @patch("vulcanus.registry.register_center.ZookeeperRegisterCenter")
    def test_register_service(self, mock_zk):
        """Test register_service returns True on success."""
        mock_center = MagicMock()
        mock_center.connected = True
        mock_center.register_service.return_value = True
        mock_zk.return_value = mock_center
        service = Service(HOSTS, RegisterCenter.ZOOKEEPER)
        result = service.register_service(SERVICE_NAME, SERVICE_INFO)
        self.assertTrue(result)

    @patch("vulcanus.registry.register_center.ZookeeperRegisterCenter")
    def test_register_service_auto_connect(self, mock_zk):
        """Test register_service auto-connects when not connected."""
        mock_center = MagicMock()
        mock_center.connected = False
        mock_center.register_service.return_value = True
        mock_zk.return_value = mock_center
        service = Service(HOSTS, RegisterCenter.ZOOKEEPER)
        result = service.register_service(SERVICE_NAME, SERVICE_INFO)
        self.assertTrue(result)
        mock_center.connect.assert_called()


class TestServiceDeleteService(unittest.TestCase):
    """Tests for Service.delete_service method."""

    @patch("vulcanus.registry.register_center.ZookeeperRegisterCenter")
    def test_delete_service(self, mock_zk):
        """Test delete_service calls center delete."""
        mock_center = MagicMock()
        mock_center.connected = True
        mock_zk.return_value = mock_center
        service = Service(HOSTS, RegisterCenter.ZOOKEEPER)
        service.delete_service(SERVICE_NAME)
        mock_center.delete_service.assert_called_once_with(SERVICE_NAME, True)


class TestServiceDisconnect(unittest.TestCase):
    """Tests for Service.disconnect method."""

    @patch("vulcanus.registry.register_center.ZookeeperRegisterCenter")
    def test_disconnect(self, mock_zk):
        """Test disconnect calls center disconnect."""
        mock_center = MagicMock()
        mock_zk.return_value = mock_center
        service = Service(HOSTS, RegisterCenter.ZOOKEEPER)
        service.disconnect()
        mock_center.disconnect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
