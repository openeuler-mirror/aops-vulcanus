#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
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
Time:
Author:
Description:
"""
import os
from abc import abstractmethod
from typing import Any, NoReturn, List
import yaml
from flask import Flask
from flask_apscheduler import APScheduler
from apscheduler.job import Job

from vulcanus.log.log import LOGGER


"""
# Timed task configuration file specification (YAML):

# Name of a scheduled task, name should be unique e.g
#   task: download security bulletin

# Task type, only 'sa_download', 'cve_scan' and 'data_correct' are supported
#   type: sa_download

# Whether scheduled tasks are allowed to run
#   enable: true

# meta info for the task, it's customised for user
#   meta:
#     cvrf_url: https://repo.openeuler.org/security/data/cvrf

# Timed config, set the scheduled time and polling policy
#   timed:
# value between 0-6, for example, 0 means Monday, 0-6 means everyday
#     day_of_week: 0-6
# value between 0-23, for example, 2 means 2:00 in a day
#     hour: 3
# Polling strategy, The value can only be 'cron' 'date' 'interval', default value is 'cron'
#     trigger: cron

- task: it's a sa downloading timed task
  type: download_sa
  enable: true
  meta:
    cvrf_url: https://repo.openeuler.org/security/data/cvrf
  timed:
    day_of_week: 0-6
    hour: 3
    trigger: cron
"""


class TimedTask:
    """
    Base class for Timed Task, all the task should inherit from this class.
    """

    timed_type = ["date", "cron", "interval"]

    def __init__(self, timed_config: dict):
        self.timed_config = timed_config
        self.task_id = timed_config['task']

    @abstractmethod
    def execute(self):
        """
        Task execute
        """
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> NoReturn:
        self.execute()

    def check(self) -> bool:
        """
        This method offers basic parameter check, you can rewrite this method if there are other check items
        """
        timed = self.timed_config.get("timed")
        trigger = timed.get("trigger")
        if trigger not in self.timed_type:
            LOGGER.error("Wrong trigger parameter for timed tasks : %s.", trigger)
            return False

        if ("day_of_week" in timed and "hour" in timed) or ("minutes" in timed):
            return True

        LOGGER.error("Missing required fields when creating scheduled task.")
        return False


class TimedTaskManager:
    """
    Class for Timed Task Management, it can add, delete, pause and view scheduled tasks.
    """

    __slots__ = ["_timed_scheduler", "_timed_config"]

    def __init__(self, app: Flask, config_path: str) -> None:
        """
        1. Init APScheduler and application
        2. read timed task config
        """
        self._timed_scheduler = APScheduler()
        self._timed_config = None
        self._init_app(app)
        if self._timed_config is None:
            self._timed_config = self._parse_config(config_path)

    @property
    def timed_scheduler(self) -> APScheduler:
        return self._timed_scheduler

    @property
    def timed_config(self) -> dict:
        return self._timed_config

    def _init_app(self, app: Flask):
        """
        Initialize APScheduler

        Args:
            app(Flask)
        """
        self.timed_scheduler.init_app(app)

    @staticmethod
    def _parse_config(file_path: str) -> dict:
        """
        Parsing the configuration file information of all timed tasks

        Args:
            file_path(str): Path to the configuration file

        Returns:
            dict: info of each task, e.g.:
                {
                    "cve scan":{
                                'name': 'cve scan',
                                'enable': true,
                                'meta': {},
                                'timed':{
                                    'day_of_week': '0-6',
                                    'hour': '2',
                                    'trigger': 'cron'
                                }

                            }
                }
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File does not exist: %s" % file_path)

        # load yaml configuration file
        with open(file_path, "r", encoding="utf-8") as file_context:
            try:
                timed_config = yaml.safe_load(file_context.read())
            except yaml.YAMLError:
                LOGGER.error("The format of the configuration file(yaml) is wrong, please check and try again")
                return dict()

        result = {}
        for config in timed_config:
            task_name = config.get("task")
            if task_name is None:
                LOGGER.warning("Missing task name for a timed task, please check")
                continue
            config["timed"]["id"] = task_name
            result[task_name] = config

        return result

    def _check(self, task: TimedTask) -> bool:
        """
        1. check whether specifiy the task type.
        2. Check whether the task has existed.

        Args:
            task(TimedTask)

        Returns:
            bool
        """
        if task.timed_config.get("type") is None:
            LOGGER.warning("Please specify the task type of [%s]", task.task_id)
            return False

        if self.get_task(task.task_id):
            LOGGER.warning("This task name [%s] already exists, ignore it", task.task_id)
            return False

        return True

    def add_job(self, task: TimedTask):
        """
        When it pass the parameter check, add the task to scheduler.

        Args:
            task(TimedTask): a task instance
        """
        if not self._check(task):
            return

        if not task.timed_config.get("enable", False):
            LOGGER.info("The task %s is configured to not start.", task.task_id)
            return

        if not task.check():
            return

        config = task.timed_config['timed']
        config['func'] = task

        self.timed_scheduler.add_job(**config)

    def get_task(self, task_id: str) -> Job:
        return self.timed_scheduler.get_job(task_id)

    @property
    def all_tasks(self) -> List[Job]:
        return self.timed_scheduler.get_jobs()

    def start(self):
        """
        Start all the scheduled tasks
        """
        self.timed_scheduler.start()

    def pause(self, task_id: str):
        """
        Pause a certain timed task according to the task id

        Args:
            task_id (str)
        """
        self.timed_scheduler.pause_job(task_id)

    def resume(self, task_id: str):
        """
        Resume a certain timed task according to the task id

        Args:
            task_id (str)
        """
        self.timed_scheduler.resume_job(task_id)

    def delete(self, task_id: str):
        """
        Delete a certain timed task according to the task id

        Args:
            task_id (str)
        """
        self.timed_scheduler.delete_job(task_id)
