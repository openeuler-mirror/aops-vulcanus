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
import os
import configparser
import inspect
import yaml

from vulcanus.conf import default_config
from vulcanus.conf.constant import SYSTEM_CONFIG_PATH, PRIVATE_INDIVIDUATION_CONFIG


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


class YamlConfigParse:
    def __init__(self, config_file, default=None):
        """
        Initialize the Config object.

        Args:
            config_file (str): Path to the YAML configuration file.
            default (module): The default configuration module (optional).
        """
        data = self.get_default_config_to_dict(default)
        data.update(self.parse_yaml(config_file))
        self.parser = JsonObject(data)

    @staticmethod
    def parse_yaml(config_file):
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
                return yaml.safe_load(file)

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

    def __str__(self) -> str:
        """
        Return a string representation of the parsed configuration.

        Returns:
            str: String representation of the parsed configuration.
        """
        return str(self.parser)


configuration = Config(SYSTEM_CONFIG_PATH, default_config)
