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
from abc import abstractmethod


class RegisterCenter:
    ZOOKEEPER = "zookeeper"
    REDIS = "redis"
    CONSUL = "consul"
    CONFIG = "config"

    meta = [ZOOKEEPER, REDIS, CONSUL, CONFIG]

    def __init__(self, hosts: str):
        try:
            host, port = hosts.split(':')
        except ValueError:
            raise ValueError('hosts format error')
        self._host = host
        self._port = int(port)

    @property
    def hosts(self):
        return f"{self._host}:{self._port}"

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def disconnect(self):
        ...
