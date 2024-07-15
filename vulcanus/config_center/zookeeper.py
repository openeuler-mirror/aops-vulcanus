from typing import Callable

from kazoo.client import KazooClient
from kazoo.protocol.states import ZnodeStat
from kazoo.recipe.watchers import DataWatch

from vulcanus.conf.constant import CONFIG_ROOT_PATH


class ZookeeperConfigCenter:
    """A class to interact with ZooKeeper configuration center."""

    root_path = CONFIG_ROOT_PATH

    def __init__(self, hosts):
        """Initialize ZookeeperConfigCenter.

        Args:
            hosts (str): The ZooKeeper server hosts.
        """
        self.zk = KazooClient(hosts=hosts)
        self.zk.start()

    def read_data(self, path):
        """Read data from the specified path in ZooKeeper.

        Args:
            path (str): The path to read data from.

        Returns:
            str: The data read from the specified path.
        """
        config_node = f"{self.root_path}/{path}"
        if not self.exists(config_node):
            return None
        data, _ = self.zk.get(config_node)
        if data:
            return data.decode('utf-8')
        return None

    def get_children_node(self, node):
        node_path = f"{self.root_path}/{node}"
        if not self.exists(node_path):
            return []

        return self.zk.get_children(node_path) or []

    def exists(self, node):
        """
        Check if the given service exists in the register center.

        Args:
            service (str): The name of the service.

        Returns:
            Optional[Any]: The nodeStat object if the node exists, None otherwise.
        """
        return self.zk.exists(node)

    def update_node(self, path, new_data):
        """Update or create a node with the given data.

        Args:
            path (str): The path of the node to update or create.
            new_data (str): The new data to set for the node.
        """
        config_node = f"{self.root_path}/{path}"
        if self.exists(config_node):
            self.zk.set(config_node, new_data.encode('utf-8'))
        else:
            self.zk.create(config_node, new_data.encode('utf-8'), makepath=True)

    def watch_config_changes(self, path: str, callback_func: Callable[[bytes, ZnodeStat], None]):
        """Watch for changes to the specified path and invoke the provided callback function.

        Args:
            path (str): The path to watch for changes.
            callback_func (Callable[[bytes, ZnodeStat], None]): The callback function to invoke when changes occur.
                The function must accept two arguments: data (bytes) and stat (ZnodeStat).
        """
        config_node = f"{self.root_path}/{path}"
        DataWatch(self.zk, config_node, callback_func)

    def delete_node(self, path, recursive=True):
        config_node = f"{self.root_path}/{path}"
        if not self.exists(config_node):
            return True
        self.zk.delete(path=config_node, recursive=recursive)
        return True

    def close_connection(self):
        """Close the connection to ZooKeeper."""
        self.zk.stop()
