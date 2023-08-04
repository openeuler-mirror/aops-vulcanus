#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import datetime as dt
import json
import os
import time
import xml
from datetime import datetime
import inspect
from functools import wraps
import xmltodict
import yaml

from vulcanus.log.log import LOGGER


def singleton(cls):
    """
    Singleton pattern decorator
    Use for create database instance
    Args:
        cls: class name

    Returns: class instance
    """
    __instance = {}

    @wraps(cls)
    def __single(*args, **kwargs):
        __key = [cls.__name__]
        __sig = inspect.signature(cls.__init__)

        for key, value in __sig.parameters.items():
            if key in kwargs:
                __key.append(kwargs[key])
            else:
                __key.append(value.default)
        __instance_key = str(__key)

        if __instance_key not in __instance:
            __instance[__instance_key] = cls(*args, **kwargs)
        return __instance[__instance_key]

    return __single


class ValidateUtils:
    """
    utils of check
    """

    @staticmethod
    def compare_two_object(obj1, obj2):
        """
        compare two complex object, dict e.g.

        Args:
            obj1: object1
            obj2: object2

        Returns:
            bool: whether equal
        """
        return obj1 == obj2 or (
            isinstance(obj1, type(obj2)) and "".join(sorted(str(obj1))) == "".join(sorted(str(obj2)))
        )

    @staticmethod
    def validate_path(path, file=True):
        """
        judge whether the path is valid.

        Args:
            path (str): path need to be checked.

        Returns:
            bool
        """
        if not os.path.exists(path):
            LOGGER.error("%s does not exist.", path)
            return False

        if not os.access(path, os.R_OK):
            LOGGER.error('Cannot access %s', path)
            return False

        if file and os.path.isdir(path):
            LOGGER.error("Couldn't parse directory %s ", path)
            return False

        return True

    @staticmethod
    def validate_time(verified_time, time_format):
        """
        judge whether the time is matched to format.

        Args:
            verified_time (str): time need to be checked.
            time_format (str): time format.

        Returns:
            bool
        """
        try:
            datetime.strptime(verified_time, time_format)
            return True
        except ValueError as error:
            LOGGER.error(error)
            return False


class TimeUtils:
    """
    time related utils
    """

    TIME_FORMAT = '%Y%m%d-%H:%M:%S'

    @classmethod
    def time_transfer(cls, start_time, end_time):
        """
        Transfer formated time to POSIX timestamp.

        Args:
            start_time (str): start time, set to 0 if None.
            end_time (str): end time, set to current time if None.

        Returns:
            tuple: e.g. (0, 1605077202)
        """
        if start_time is None:
            start_time = 0
        else:
            if '-' not in start_time:
                start_time += '19000101-00:00:00'
            if not ValidateUtils.validate_time(start_time, cls.TIME_FORMAT):
                LOGGER.error('The start time format is not correct, please refer to %s', cls.TIME_FORMAT)
                return

            start_time_struct = datetime.strptime(start_time, cls.TIME_FORMAT)
            # Return integer POSIX timestamp.
            start_time = max(int(start_time_struct.timestamp()), 0)

        now = int(time.time())

        if end_time is None:
            # if end time is not specified, use the current time
            end_time = now
        else:
            if '-' not in end_time:
                end_time += '21001230-23:59:59'
            if not ValidateUtils.validate_time(end_time, cls.TIME_FORMAT):
                LOGGER.error('The end time format is not correct, please refer to %s', cls.TIME_FORMAT)
                return

            end_time_struct = datetime.strptime(end_time, cls.TIME_FORMAT)
            end_time = min(int(end_time_struct.timestamp()), now)

        if start_time > end_time:
            LOGGER.error('The time range is not correct, please check again.')
            return

        return start_time, end_time

    @classmethod
    def time_check_generate(cls, starttime, endtime):
        """
        Description: check and generate time

        Args:
            starttime: starttime of the command
            endtime: endtime of the command
        Returns:
            [starttime, endtime]: list of starttime and endtime
        """
        if all([starttime, endtime]):
            if not ValidateUtils.validate_time(endtime, cls.TIME_FORMAT):
                LOGGER.error('The start time format is not correct, please refer to %s', cls.TIME_FORMAT)
                return
            if not ValidateUtils.validate_time(starttime, cls.TIME_FORMAT):
                LOGGER.error('The start time format is not correct, please refer to %s', cls.TIME_FORMAT)
                return
        else:
            if any([starttime, endtime]):
                if not starttime:
                    starttime = datetime.strptime(endtime, cls.TIME_FORMAT) + dt.timedelta(hours=-1)
                if not endtime:
                    endtime = datetime.strptime(starttime, cls.TIME_FORMAT) + dt.timedelta(hours=+1)
            else:
                endtime = datetime.now()
                starttime = endtime + dt.timedelta(hours=-1)

        starttime = starttime if isinstance(starttime, str) else starttime.strftime(cls.TIME_FORMAT)
        endtime = endtime if isinstance(endtime, str) else endtime.strftime(cls.TIME_FORMAT)
        starttime, endtime = cls.time_transfer(starttime, endtime)

        return [starttime, endtime]


class ConfigFileParse:
    @staticmethod
    def read_yaml_config_file(config_file):
        """
        Read yaml configuration file.

        Args:
            config_file (str): the configuration file path

        Returns:
            dict/None
        """
        conf = None
        if config_file is None:
            return conf

        if ValidateUtils.validate_path(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as file_io:
                    conf = yaml.safe_load(file_io.read())
                    if not isinstance(conf, (dict, list)):
                        LOGGER.error("YAML [%s] didn't produce a dictionary or list.", config_file)
                        conf = None
            except yaml.scanner.ScannerError:
                LOGGER.error("Couldn't parse yaml %s ", config_file)

        return conf

    @staticmethod
    def read_json_config_file(config_file):
        """
        Read json configuration file.

        Args:
            config_file (str): the configuration file path

        Returns:
            dict/None
        """
        conf = None
        if config_file is None:
            return conf

        if ValidateUtils.validate_path(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as file_io:
                    conf = json.load(file_io)
            except json.decoder.JSONDecodeError as error:
                LOGGER.error('%s in %s', str(error), config_file)

        return conf

    @staticmethod
    def read_xml_config_file(config_file):
        """
        Read xml configuration file.

        Args:
            config_file (str): the configuration file path

        Returns:
            dict/None
        """
        conf = None
        if config_file is None:
            return conf

        if ValidateUtils.validate_path(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as file_io:
                    xml_parse = xmltodict.parse(file_io.read())
                    conf = json.loads(json.dumps(xml_parse))
            except xml.parsers.expat.ExpatError:
                LOGGER.error('%s parsed failed.', config_file)

        return conf
