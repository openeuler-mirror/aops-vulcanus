#!/usr/bin/python3
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
Time:
Author:
Description: global config.
"""
import configparser
import inspect
import logging
import os
from functools import partial

import yaml
from kazoo.exceptions import KazooException

from vulcanus.conf.constant import (
    PRIVATE_INDIVIDUATION_CONFIG,
    DEFAULT_CUSTOM_CONF_DIR_PATH,
    GLOBAL_CONFIG_PATH,
)
from vulcanus.config_center.zookeeper import ZookeeperConfigCenter


class Config:
    """
    Merge system default configuration with configuration file.
    """

    def __init__(self, config_file, default=None):
        """
        Class instance initialization.

        Args:
            config_file(str): configuration file
            default(module): module of default configuration
        """
        # read default configuration
        if default is not None:
            for config in dir(default):
                setattr(self, config, getattr(default, config))

        self.read_config(config_file)

    def _load_conf(self, config_file):
        if not os.path.exists(config_file):
            raise RuntimeError(f"Configuration file does not exist: {config_file}")

        conf = configparser.RawConfigParser()
        try:
            conf.read(config_file)
        except configparser.ParsingError:
            raise RuntimeError(f"Failed to load the configuration file: {config_file}")

        return conf

    def _load_private_config(self, config_file=PRIVATE_INDIVIDUATION_CONFIG):
        """
        Load user-private personalization settings

        Args:
            config_file: private config file
        """
        conf = self._load_conf(config_file)

        for section in conf.sections():
            self._set_section_value(conf, section)

    def _set_section_value(self, conf, section):
        temp_config = dict()
        for option in conf.items(section):
            try:
                (key, value) = option
            except IndexError:
                continue
            if not value:
                continue
            if value.isdigit():
                value = int(value)
            elif value.lower() in ("true", "false"):
                value = True if value.lower() == "true" else False
            temp_config[key.upper()] = value

        if not temp_config:
            return
        # let default configuration be merged with configuration from config file
        if hasattr(self, section):
            getattr(self, section).update(temp_config)
        else:
            setattr(self, section, temp_config)

    def read_config(self, config_file):
        """
        read configuration from file.

        Args:
            config_file(str): configuration file
        """

        conf = self._load_conf(config_file)

        for section in conf.sections():
            self._set_section_value(conf, section)

        self._load_private_config()


class JsonObject:
    def __init__(self, data):
        """
        Initialize the JsonObject object.

        Args:
            data (dict): Data to be converted to a JsonObject.
        """
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, JsonObject(value))
            elif isinstance(value, list):
                setattr(self, key, [JsonObject(v) if isinstance(v, dict) else v for v in value])
            else:
                setattr(self, key, value)

    def __getattr__(self, attr):
        return self.__dict__.get(attr)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class ConfigHandle:
    """Handles configuration parsing and management."""

    def __init__(self, config_name: str = None, default=None):
        """
        Initialize the Config object.

        Args:
            config_file (str): Path to the YAML configuration file.
            default (module): The default configuration module (optional).
        """
        self.config_obj = None
        self.config_center = None
        self.global_config_data = {}
        self.custom_config_data = {}
        self.custom_config_file_name = config_name

        self.json_config_data = self.get_default_config_to_dict(default) if default else {}
        self.parser = JsonObject(self.json_config_data)
        self.handle()

    @staticmethod
    def parse_yaml_from_yaml_file(config_file: str):
        """
        Parse the YAML configuration file and return the parsed data.

        Args:
            config_file (str): Path to the YAML configuration file.

        Returns:
            Any: Parsed data from the YAML configuration file.

        Raises:
            RuntimeError: If the configuration file does not exist or fails to load.
        """
        if not os.path.exists(config_file):
            raise RuntimeError(f"Configuration file does not exist: {config_file}")
        try:
            with open(config_file, 'r') as file:
                return yaml.safe_load(file) or dict()

        except IOError:
            raise RuntimeError(f"Failed to load the configuration file: {config_file}")

        except yaml.YAMLError:
            raise RuntimeError(f"Failed to parse the configuration file: {config_file}")

    @staticmethod
    def get_default_config_to_dict(default_config_module):
        """
        Convert variables defined in a default configuration module to a dictionary.

        Args:
            default_config_module (module): The default configuration module.

        Returns:
            dict: Dictionary containing the variables and their values defined in the default configuration module.
        """
        default_config_dict = {}

        if default_config_module is None:
            return default_config_dict

        for name, value in inspect.getmembers(default_config_module):
            if not name.startswith("__") and not inspect.ismodule(value):
                default_config_dict[name] = value
        return default_config_dict

    def _parse_global_config_data(self, data: dict):

        if data:
            data.update(
                {
                    **data.pop("infrastructure", {}),
                    **data.pop("services", {}),
                }
            )
            return data
        return {"include": DEFAULT_CUSTOM_CONF_DIR_PATH}

    def merge_custom_config(self):
        """Merge custom configuration data into the global configuration."""
        for field, value in self.custom_config_data.items():
            if field in self.json_config_data and value is not None:
                self.json_config_data[field] = value
            elif field not in self.json_config_data:
                self.json_config_data[field] = value

    def load_global_config(self):
        """Parse and update global configuration data."""
        global_config_data = self.parse_yaml_from_yaml_file(GLOBAL_CONFIG_PATH)
        self.json_config_data.update(self._parse_global_config_data(global_config_data))

    def load_custom_config(self):
        """Load and merge custom configuration data if the custom config file exists."""
        custom_config_path = f"{self.json_config_data.get('include')}/{self.custom_config_file_name}.yml"
        if os.path.exists(custom_config_path):
            self.custom_config_data = self.parse_yaml_from_yaml_file(custom_config_path)
            self.merge_custom_config()

    def handle(self):
        """
        Handle configuration loading and parsing.

        Raises:
            RuntimeError: If there's an error parsing or loading configuration files.
        """

        self.load_global_config()
        if self.custom_config_file_name:
            self.load_custom_config()
        self.parser = JsonObject(self.json_config_data)

    def reload(self):
        """Reload configuration."""
        self.parser = JsonObject(self.json_config_data)

    def add_listener(self, watch_node, save_path):
        """
        Add a listener to monitor changes in a configuration node.

        Args:
            watch_node (str): Node to watch.
            save_path (str): Path to save the configuration data.`

        Example:
        To listen to changes in the 'global' node and save the configuration data to 'aops-config.yml':

        ```python
        config_obj = ConfigHandle(None)
        config_obj.add_listener(watch_node='global', save_path='aops-config.yml')
        ```
        """
        partial_listener = partial(self._watch_node_changes, save_path=save_path)
        try:
            # Establish connection with configuration center if not already done
            if not self.config_center:
                zookeeper_host = self.json_config_data.get("zookeeper").get("host")
                zookeeper_port = self.json_config_data.get("zookeeper").get("port")
                if not zookeeper_host or not zookeeper_port:
                    raise RuntimeError("Failed to get zookeeper config info")
                self.config_center = ZookeeperConfigCenter(f"{zookeeper_host}:{zookeeper_port}")
            self.config_center.watch_config_changes(watch_node, partial_listener)
        except KazooException as e:
            raise RuntimeError(f"Failed to add listener for watching node {watch_node}") from e

    def _watch_node_changes(self, data, stat, save_path):
        """
        Callback function to save configuration data to local file when Zookeeper node changes.

        Args:
            data: Configuration data received from Zookeeper node.
            stat: Node status.
            save_path (str): Path to save the configuration data.
        """
        if not data:
            return

        with open(save_path, "wb") as f:
            f.write(data)

        tmp_data = data.decode("utf8")
        if self.is_valid_yaml(tmp_data):
            if save_path == GLOBAL_CONFIG_PATH:
                wait_to_update_config = self._parse_global_config_data(yaml.safe_load(tmp_data))
                wait_to_update_config.update(self.custom_config_data)
                self.json_config_data.update(wait_to_update_config)
            else:
                wait_to_update_config = yaml.safe_load(tmp_data)
                self.custom_config_data = wait_to_update_config
                self.json_config_data.update(wait_to_update_config)
            self.reload()
        else:
            logging.error("Failed to load configuration data from config center")

    def is_valid_yaml(self, yaml_str: str) -> bool:
        """
        Check the correctness of yaml format.

        Args:
            yaml_str (str): yaml string

        Returns:
            bool: Returns true if the yaml format is correct, otherwise returns false.
        """
        try:
            yaml.safe_load(yaml_str)
            return True
        except yaml.YAMLError as e:
            logging.warning(f"Wrong yaml data: {e}")
            return False

    def __str__(self) -> str:
        """
        Return a string representation of the parsed configuration.

        Returns:
            str: String representation of the parsed configuration.
        """
        return str(JsonObject(self.json_config_data))


config_obj = ConfigHandle(config_name=None)
configuration = config_obj.parser
