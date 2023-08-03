#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
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
Time: 2022-07-27
Author: YangYunYi
Description: build inventory
"""

import pandas as pd
import yaml
from pathlib import Path

CURRENT_PATH = Path(__file__).parent
CONF_PATH = CURRENT_PATH / "conf"
HOST_INFO_FILE = CONF_PATH / "import_host.xls"
INVENTORY_CONFIG_FILE = CONF_PATH / "inventory_config.yml"
OUTPUT_DIR = CURRENT_PATH / "output"


def parse_host_info(file_path: Path, component_list: list) -> dict:
    """
    Parse host info from the Excel file and return a dictionary.

    Args:
        file_path (Path): Path to the Excel file containing host information.
        component_list (list): List of components to install.

    Returns:
        component_dict_list (dict): Component info as a dictionary.
    """
    component_dict_list = {}
    for component in component_list:
        component_sheet = pd.read_excel(file_path, sheet_name=component)
        component_dict_list[f"{component}_hosts"] = {
            "hosts": {row.host_name: row.drop("host_name").to_dict() for _, row in component_sheet.iterrows()},
        }
        component_dict_list[f"{component}_hosts"]["hosts"] = {
            host_name: {**host_data, "ansible_python_interpreter": "/usr/bin/python3"}
            for host_name, host_data in component_dict_list[f"{component}_hosts"]["hosts"].items()
        }

    return component_dict_list


def dump_to_yaml(component_dict_list: dict, inventory_config_list: dict) -> None:
    """
    Save inventory info to inventory yaml files.

    Args:
        component_dict_list (dict): Host component info.
        inventory_config_list (dict): Inventory config list.

    Returns:
        None
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    for component, component_info in inventory_config_list.items():
        hosts_info_json = {host_info: component_dict_list.get(host_info) for host_info in component_info if host_info in component_dict_list}
        inventory_file_path = OUTPUT_DIR / component
        with inventory_file_path.open("w", encoding="utf-8") as inventory_file:
            yaml.dump(hosts_info_json, inventory_file)


def build_inventory() -> None:
    """
    Build inventory file entry.

    Args:
        None

    Returns:
        None
    """
    with INVENTORY_CONFIG_FILE.open("r") as inventory_cfg:
        inventory_config_list = yaml.safe_load(inventory_cfg)
        component_list = list(inventory_config_list.keys())
        component_dict_list = parse_host_info(HOST_INFO_FILE, component_list)
        dump_to_yaml(component_dict_list, inventory_config_list)


if __name__ == "__main__":
    build_inventory()
