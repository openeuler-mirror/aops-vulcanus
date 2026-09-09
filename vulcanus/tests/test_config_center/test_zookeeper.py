# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2023. All rights reserved.
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
Description: unit tests for config_center/zookeeper.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vulcanus.config_center.zookeeper import ZookeeperConfigCenter

HOSTS = "127.0.0.1:2181"
NODE_PATH = "test_node"
NODE_DATA = "test_data"
CONFIG_PATH = "/aops/config"


class TestZookeeperConfigCenterInit(unittest.TestCase):
    """Tests for ZookeeperConfigCenter initialization."""

    @patch("vulcanus.config_center.zookeeper.KazooClient")
    def test_init(self, mock_kazoo):
        """Test ZookeeperConfigCenter initializes with hosts."""
        mock_client = MagicMock()
        mock_kazoo.return_value = mock_client
        center = ZookeeperConfigCenter(HOSTS)
        mock_client.start.assert_called_once()


class TestZookeeperConfigCenterReadData(unittest.TestCase):
    """Tests for ZookeeperConfigCenter.read_data method."""

    @patch("vulcanus.config_center.zookeeper.KazooClient")
    def test_read_data_exists(self, mock_kazoo):
        """Test read_data returns decoded data when node exists."""
        mock_client = MagicMock()
        mock_client.exists.return_value = True
        mock_client.get.return_value = (NODE_DATA.encode("utf-8"), None)
        mock_kazoo.return_value = mock_client
        center = ZookeeperConfigCenter(HOSTS)
        result = center.read_data(NODE_PATH)
        self.assertEqual(result, NODE_DATA)

    @patch("vulcanus.config_center.zookeeper.KazooClient")
    def test_read_data_not_exists(self, mock_kazoo):
        """Test read_data returns None when node doesn't exist."""
        mock_client = MagicMock()
        mock_client.exists.return_value = None
        mock_kazoo.return_value = mock_client
        center = ZookeeperConfigCenter(HOSTS)
        result = center.read_data(NODE_PATH)
        self.assertIsNone(result)


class TestZookeeperConfigCenterUpdateNode(unittest.TestCase):
    """Tests for ZookeeperConfigCenter.update_node method."""

    @patch("vulcanus.config_center.zookeeper.KazooClient")
    def test_update_existing_node(self, mock_kazoo):
        """Test update_node sets data on existing node."""
        mock_client = MagicMock()
        mock_client.exists.return_value = True
        mock_kazoo.return_value = mock_client
        center = ZookeeperConfigCenter(HOSTS)
        center.update_node(NODE_PATH, NODE_DATA)
        mock_client.set.assert_called_once()

    @patch("vulcanus.config_center.zookeeper.KazooClient")
    def test_update_new_node(self, mock_kazoo):
        """Test update_node creates new node when not exists."""
        mock_client = MagicMock()
        mock_client.exists.return_value = None
        mock_kazoo.return_value = mock_client
        center = ZookeeperConfigCenter(HOSTS)
        center.update_node(NODE_PATH, NODE_DATA)
        mock_client.create.assert_called_once()


class TestZookeeperConfigCenterDeleteNode(unittest.TestCase):
    """Tests for ZookeeperConfigCenter.delete_node method."""

    @patch("vulcanus.config_center.zookeeper.KazooClient")
    def test_delete_existing_node(self, mock_kazoo):
        """Test delete_node deletes existing node."""
        mock_client = MagicMock()
        mock_client.exists.return_value = True
        mock_kazoo.return_value = mock_client
        center = ZookeeperConfigCenter(HOSTS)
        result = center.delete_node(NODE_PATH)
        self.assertTrue(result)
        mock_client.delete.assert_called_once()

    @patch("vulcanus.config_center.zookeeper.KazooClient")
    def test_delete_nonexistent_node(self, mock_kazoo):
        """Test delete_node returns True for non-existent node."""
        mock_client = MagicMock()
        mock_client.exists.return_value = None
        mock_kazoo.return_value = mock_client
        center = ZookeeperConfigCenter(HOSTS)
        result = center.delete_node(NODE_PATH)
        self.assertTrue(result)


class TestZookeeperConfigCenterGetChildren(unittest.TestCase):
    """Tests for ZookeeperConfigCenter.get_children_node method."""

    @patch("vulcanus.config_center.zookeeper.KazooClient")
    def test_get_children_exists(self, mock_kazoo):
        """Test get_children_node returns children list."""
        mock_client = MagicMock()
        mock_client.exists.return_value = True
        mock_client.get_children.return_value = ["child1", "child2"]
        mock_kazoo.return_value = mock_client
        center = ZookeeperConfigCenter(HOSTS)
        result = center.get_children_node(NODE_PATH)
        self.assertEqual(result, ["child1", "child2"])

    @patch("vulcanus.config_center.zookeeper.KazooClient")
    def test_get_children_not_exists(self, mock_kazoo):
        """Test get_children_node returns empty list."""
        mock_client = MagicMock()
        mock_client.exists.return_value = None
        mock_kazoo.return_value = mock_client
        center = ZookeeperConfigCenter(HOSTS)
        result = center.get_children_node(NODE_PATH)
        self.assertEqual(result, [])


class TestZookeeperConfigCenterClose(unittest.TestCase):
    """Tests for ZookeeperConfigCenter.close_connection method."""

    @patch("vulcanus.config_center.zookeeper.KazooClient")
    def test_close_connection(self, mock_kazoo):
        """Test close_connection stops the client."""
        mock_client = MagicMock()
        mock_kazoo.return_value = mock_client
        center = ZookeeperConfigCenter(HOSTS)
        center.close_connection()
        mock_client.stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
