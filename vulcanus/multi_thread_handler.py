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
import os
from typing import List, NoReturn
from concurrent.futures import ThreadPoolExecutor, as_completed

from vulcanus.log.log import LOGGER


class MultiThreadHandler:
    """
    A general multi-threaded execution method.

    """

    def __init__(self, func, tasks, workers):
        """
        Init multi thread handler

        Args:
            func:   function that needs to be executed.
            tasks:  An iterable object contains sets of
                    parameters that need to be executed.
        """
        self._func = func
        self._tasks = tasks
        self._workers = workers
        self._thread_pool = []

    @property
    def thread_pool(self):
        return self._thread_pool

    @property
    def tasks(self):
        return self._tasks

    @property
    def func(self):
        return self._func

    @property
    def workers(self):
        return self._workers

    def create_thread(self, call_back=None) -> NoReturn:
        """
            Create thread

        Args:
            call_back: the callback function
            1. A callable object that will be called with the future as its
            only argument when the future completes or is cancelled.
            2. You can get thread execution result by future.result().

        """
        if len(self.tasks) == 0:
            LOGGER.error("The count of tasks is zero, " "please check and try again.")
            return

        if not self._workers:
            self._workers = len(self.tasks) if len(self.tasks) < os.cpu_count() else os.cpu_count() * 2

        with ThreadPoolExecutor(max_workers=self.workers) as thread_pool:
            for task in self._tasks:
                future = thread_pool.submit(self._func, task)
                if call_back:
                    future.add_done_callback(call_back)
                self._thread_pool.append(future)

    def get_result(self, completed_timeout=None, future_timeout=None) -> List:
        """
            Get the execution results of all threads.

        Args:
            completed_timeout (int): The maximum number of seconds to wait,
                if the result iterator can't be generated before the given
                timeout, it will raise TimeoutError.
            future_timeout(int): The number of seconds to wait for the result,
                if the future isn't done. if the future didn't execute before
                the given timeout, it will raise TimeoutError.

        Returns:
            result list: List[result of func]
        """
        res = []
        for future in as_completed(self._thread_pool, timeout=completed_timeout):
            try:
                res.append(future.result(timeout=future_timeout))
            except TypeError as e:
                LOGGER.error("An error occurred during thread execution " "due to incorrect parameter.")
                res.append({"message": str(e)})

            except Exception:
                LOGGER.warning("An error occurred during thread execution," "please check and try again.")
                res.append({"message": future.exception()})

        return res
